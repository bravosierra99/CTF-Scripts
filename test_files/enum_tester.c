#include <stdio.h>
#include <string.h>

void main(int argc, char *argv[]) {
    char* argument = argv[1];
    char* password = "Im_a_password_fool";
    if (strlen(argument) != strlen(password)){
        printf("nope");
        return;
    }
    int a, b,i;
    for (i = 0; i++; i < 100){
        a = b;
        b = i;
        a = a * b;
        b = 10 - a + b;
    }
    if (!strcmp(argument, password)){
        
        printf("%iCongrats, you have totally gotten this correct",a);
    } else {
        printf("%istill nope");
    }
    return;
}
