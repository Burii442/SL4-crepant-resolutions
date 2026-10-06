"""Private Sage cache paths, including when an output directory has spaces.

Sage's external GAP interface cannot reliably use a DOT_SAGE containing
whitespace. Only disposable runtime files move to a fresh private directory;
all proof inputs, logs, manifests and certificates remain in the chosen output.
"""
from pathlib import Path
import os,shutil,tempfile,signal,time


def safe_path(path):
    return not any(c.isspace() for c in str(path))


def terminate_owned_process_group(process,registered_groups,grace_seconds=2.0):
    """Stop one group created by this runner with start_new_session=True.

    The leader may already have exited while a descendant holds stdout open.
    Wait for the group, not just its leader, before deciding whether KILL is
    needed. The registration is private to the caller that created the group;
    never accept an arbitrary external PID as an owned process group.
    """
    group=int(process.pid)
    assert group in registered_groups and group>1 and group!=os.getpgrp(), 'Only a registered child process group may be terminated'
    grace_seconds=float(grace_seconds)
    assert 0<=grace_seconds<=10, 'Process-group grace period must be bounded'
    def alive():
        process.poll()  # Reap an exited leader before testing the entire group.
        try:os.killpg(group,0)
        except ProcessLookupError:return False
        return True
    signals=[]
    try:
        for signum in [signal.SIGTERM,signal.SIGKILL]:
            if not alive():break
            try:os.killpg(group,signum)
            except ProcessLookupError:break
            signals.append(signal.Signals(signum).name)
            deadline=time.monotonic()+grace_seconds
            while alive() and time.monotonic()<deadline:time.sleep(0.02)
        return {'process_group':group,'signals':signals,'whole_process_group_exited':not alive(),
                'leader_returncode':process.poll()}
    except OSError as error:
        # Permission restrictions must neither hide the original interruption
        # nor turn an unverified group termination into a successful claim.
        return {'process_group':group,'signals':signals,'whole_process_group_exited':False,
                'leader_returncode':process.poll(),'termination_error':str(error)}


class SageCache:
    def __init__(self,path,ownership):
        self.path=Path(path).resolve()
        self.ownership=ownership

    def metadata(self):
        return {'path':str(self.path),'ownership':self.ownership,
                'whitespace_free':safe_path(self.path)}

    def cleanup(self,process_groups=()):
        """Never delete a private cache while a known process group survives."""
        if self.ownership!='temporary':
            return {'status':'RETAINED_WITH_OUTPUT' if self.ownership=='output' else 'INHERITED_NOT_OWNED'}
        for group in set(process_groups):
            try:os.killpg(int(group),0)
            except ProcessLookupError:continue
            except PermissionError:
                return {'status':'RETAINED_PROCESS_GROUP_STATE_UNKNOWN','process_group':int(group)}
            else:
                return {'status':'RETAINED_LIVE_PROCESS_GROUP','process_group':int(group)}
        try:shutil.rmtree(self.path)
        except OSError as error:
            return {'status':'RETAINED_CLEANUP_ERROR','error':str(error)}
        return {'status':'REMOVED_AFTER_PROCESS_GROUPS_EXITED'}


def allocate_sage_cache(preferred,inherited=None):
    """Use a private output cache, or a fresh whitespace-free temporary path.

    Nested runners may inherit the parent's already safe cache. An inherited
    cache is never removed by the child runner.
    """
    if inherited and safe_path(Path(inherited).expanduser().resolve()):
        return SageCache(Path(inherited).expanduser(),'inherited')
    preferred=Path(preferred).resolve()
    if safe_path(preferred):
        preferred.mkdir(parents=True,exist_ok=True,mode=0o700)
        return SageCache(preferred,'output')
    candidates=[Path(tempfile.gettempdir()),Path('/tmp')]
    for base in candidates:
        if not safe_path(base.resolve()) or not base.is_dir():continue
        try:path=Path(tempfile.mkdtemp(prefix='asl4-sage-cache-',dir=base))
        except OSError:continue
        assert safe_path(path.resolve())
        return SageCache(path,'temporary')
    raise RuntimeError('Sage requires a writable temporary cache directory without whitespace')
