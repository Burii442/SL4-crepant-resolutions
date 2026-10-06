"""Reject false, missing, duplicate and error-marked Singular proof outputs.

Run with sage -python. These are protocol tests, not invariant-ring proofs.
"""
import unittest
from small_ci import check_protocol


def successful_output(case):
    degree = 12 if case == 140 else 10
    weights = [2,2,6,6,6,6] if case == 140 else [2,2,4,6,5,5]
    entries = [('INDEX',[case]),('EXPLICIT_GENERATORS_MATCH_FINVAR',[1]),
               ('DISPLAYED_RELATIONS_SUBSTITUTE_TO_ZERO',[1]),
               ('NUMBER_OF_INVARIANT_GENERATORS',[6]),('NUMBER_OF_MINIMAL_RELATIONS',[2]),
               ('QUOTIENT_DIMENSION',[4]),('EMBEDDING_DIMENSION_AT_ORIGIN',[6]),
               ('MINIMAL_EMBEDDING_PASS',[1]),('INVARIANT_AUDIT_PASS',[1]),
               ('PRINTED_RELATIONS_IN_FULL_KERNEL',[1]),('FULL_KERNEL_IN_PRINTED_RELATIONS',[1]),
               ('DHZ_COMPLETE',[1]),('GENERATOR_DEGREES',weights),
               ('MINIMAL_RELATION_DEGREES',[degree,degree]),('MINIMAL_RELATION_M_ADIC_ORDERS',[2,2])]
    return '\n'.join(marker+'\n'+'\n'.join(map(str,values)) for marker,values in entries)+'\n'


class ProtocolTests(unittest.TestCase):
    def test_complete_protocol(self):
        for case in [140,243]:check_protocol(successful_output(case),case)

    def test_every_required_scalar_can_fail(self):
        for case in [140,243]:
            text = successful_output(case)
            for marker,expected in check_protocol(text,case).items():
                with self.subTest(case=case,marker=marker):
                    bad = text.replace(marker+'\n'+str(expected)+'\n',marker+'\n99999\n')
                    with self.assertRaises(AssertionError):check_protocol(bad,case)

    def test_missing_duplicate_and_error(self):
        text = successful_output(140)
        for bad in [text.replace('DHZ_COMPLETE\n1\n',''),text+'DHZ_COMPLETE\n1\n',
                    text+'   ? error in polynomial computation\n',
                    text.replace('MINIMAL_RELATION_M_ADIC_ORDERS\n2\n2',
                                 'MINIMAL_RELATION_M_ADIC_ORDERS\n1\n2')]:
            with self.assertRaises(AssertionError):check_protocol(bad,140)


if __name__=='__main__':unittest.main()
