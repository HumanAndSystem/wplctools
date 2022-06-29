#include <iostream>

#include "_lexer.h"

int main() {
    std::cout << "test" << std::endl;
    lexer l;
    l.scan("D1111");
    l.scan("X1234");
    l.scan("WF.2");
    l.scan("WF.F");
    l.scan("K2M1");
}
