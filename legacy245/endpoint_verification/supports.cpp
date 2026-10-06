// Exhaustive branch-and-propagate outer bound for supports of an affine variety.
// Input contains a list of monomial support masks for EVERY defining polynomial.
// A polynomial at an actual point cannot have exactly one surviving monomial.
// Duplicate masks are retained: different monomials with the same support count.
// Both branches of each unforced Boolean variable are visited; there is no pruning
// based on an unproved geometric condition, random choice, time limit, or cache.
#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include <cstdint>
using U=uint64_t;
std::vector<std::vector<U>> patterns;
std::vector<unsigned> weight;
U allbits,nodes=0,solutions=0;int n;
void visit(U yes,U no){
 ++nodes;bool changed;
 do{
  changed=false;
  for(auto const& p:patterns){
   unsigned count=0,sure=0;U only=0,other=0;unsigned others=0;
   for(U m:p)if(!(m&no)){
    ++count;only=m;
    if((m&yes)==m)++sure;else{++others;other=m;}
   }
   if(!count || sure>=2)continue;
   if(count==1){
    U unknown=only&~yes;
    if(!unknown)return;
    if((unknown&(unknown-1))==0){no|=unknown;changed=true;}
   }else if(sure==1 && others==1){
    U force=other&~yes;
    if(force&no)return;
    if(force){yes|=force;changed=true;}
   }
  }
 }while(changed);
 U unset=allbits&~(yes|no);
 if(!unset){++solutions;std::cout<<yes<<'\n';return;}
 int chosen=-1;for(int j=0;j<n;++j)if((unset&(U(1)<<j))&&(chosen<0 || weight[j]>weight[chosen]))chosen=j;
 U b=U(1)<<chosen;visit(yes|b,no);visit(yes,no|b);
}
int main(int argc,char**argv){
 if(argc!=2)return 2;std::ifstream in(argv[1]);unsigned count;in>>n>>count;
 if(!in || n<1 || n>62)return 3;allbits=(U(1)<<n)-1;weight.assign(n,0);
 while(count--){unsigned size;in>>size;std::vector<U> p(size);for(auto &m:p)in>>m;std::sort(p.begin(),p.end());patterns.push_back(p);}
 if(!in)return 4;
 std::sort(patterns.begin(),patterns.end());patterns.erase(std::unique(patterns.begin(),patterns.end()),patterns.end());
 std::sort(patterns.begin(),patterns.end(),[](auto const&a,auto const&b){return a.size()<b.size();});
 for(auto const&p:patterns)for(U m:p)for(int j=0;j<n;++j)if(m&(U(1)<<j))++weight[j];
 visit(0,0);std::cerr<<"EXHAUSTIVE_SUPPORTS "<<solutions<<" BRANCH_NODES "<<nodes<<'\n';return 0;
}
