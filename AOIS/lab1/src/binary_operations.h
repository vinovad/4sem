#ifndef OPERATIONS_H
#define OPERATIONS_H

#include "convert_binary.h"

namespace Binary {

    class BinaryOperations {
    public:
        // Сложение в дополнительном коде
        static BinaryRegister addTwosComplement(
            const BinaryRegister& first,
            const BinaryRegister& second);

        // Вычитание через дополнительный код (first - second)
        static BinaryRegister subtractTwosComplement(
            const BinaryRegister& first,
            const BinaryRegister& second);

        // Умножение в прямом коде
        static BinaryRegister multiplySignMagnitude(
            const BinaryRegister& first,
            const BinaryRegister& second);

        // Деление в прямом коде с точностью до 5 двоичных знаков
        static BinaryRegister divideSignMagnitude(
            const BinaryRegister& first,
            const BinaryRegister& second);
    };

}

#endif