#include <iostream>

using namespace std;

int main(){
    for(int i=10; i>=-5; i--){
        cout<<i<<endl;
    }
    int product=1;
    for(int x=1; x<10; x++){
        product=product*x;
    }
    cout<<product<<endl;

    int num1=0;
    int num2=0;
    cout<<"Enter 2 numbers: ";
    cin>>num1;
    cin>>num2;
    if(num1>num2)
        cout<<num1<<" is bigger"<<endl;
    else if(num2>num1)
        cout<<num2<<" is bigger"<<endl;
    else
        cout<<"They are the same"<<endl;

}