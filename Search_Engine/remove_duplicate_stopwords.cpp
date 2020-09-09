#include<bits/stdc++.h>
using namespace std;
int main()
{
    freopen("sncs.txt" , "r" , stdin);
    freopen("out.txt" , "w" , stdout);
    set<string> s;
    while(1){
        string x;
        cin >> x;
        s.insert(x);
        if(x.length() == 0) break;
    }
    for(auto x : s){
        cout << x << endl ;
    }
	return 0; 
}
