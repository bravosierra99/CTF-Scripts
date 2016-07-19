#include <stdio.h>
#include <string.h>

void main(int argc, char *argv[]) {
    char* argument = argv[1];
    char* password = "Im_a_password_fool";
    if (strlen(argument) != strlen(password)){
        printf("nope\n");
        return;
    }
    int i;
    printf("what the hell is going on here\n");
    for(i = 0;  i < strlen(password);i++){
        printf("in the loop %i\n",i);
        if (argument[i] != password[i]){
            printf("%c   %c",argument[i],password[i]);
            return;
        }
            printf("%c   %c",argument[i],password[i]);
    }
        
    printf("Congrats, you have totally gotten this correct\n");
}
