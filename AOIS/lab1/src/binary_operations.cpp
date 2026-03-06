#include "binary_operations.h"
#include <iostream>

namespace Binary {

static const int REGISTER_BIT_SIZE = 32;
static const int REGISTER_LAST_BIT = 31;
static const int REGISTER_FIRST_MAG_BIT = 1;
static const int FRACTIONAL_BITS_COUNT  = 5;

static unsigned long long readMagnitude(const BinaryRegister& reg) {
    unsigned long long magnitude = 0;
    for (int index = REGISTER_FIRST_MAG_BIT; index < REGISTER_BIT_SIZE; index++) {
        magnitude = (magnitude << 1) | static_cast<unsigned long long>(reg.getBit(index));
    }
    return magnitude;
}

static int computeResultSign(const BinaryRegister& first, const BinaryRegister& second) {
    return first.getBit(0) ^ second.getBit(0);
}

static BinaryRegister packSignMagnitude(int sign, unsigned long long magnitude) {
    BinaryRegister result;
    result.setBit(0, sign);
    for (int index = REGISTER_LAST_BIT; index >= REGISTER_FIRST_MAG_BIT; index--) {
        result.setBit(index, static_cast<int>(magnitude & 1));
        magnitude >>= 1;
    }
    return result;
}

// Задание 2: Сложение двух чисел в дополнительном коде
BinaryRegister BinaryOperations::addTwosComplement(
    const BinaryRegister& first,
    const BinaryRegister& second)
{
    BinaryRegister result;
    int carry = 0;
    for (int index = REGISTER_LAST_BIT; index >= 0; index--) {
        int sum = first.getBit(index) + second.getBit(index) + carry;
        result.setBit(index, sum % 2);
        carry = sum / 2;
    }
    return result;
}

// Задание 3: Вычитание в дополнительном коде (first - second)
BinaryRegister BinaryOperations::subtractTwosComplement(
    const BinaryRegister& first,
    const BinaryRegister& second)
{
    BinaryRegister negatedSecond;
    for (int index = 0; index < REGISTER_BIT_SIZE; index++) {
        negatedSecond.setBit(index, 1 - second.getBit(index));
    }
    int carry = 1;
    for (int index = REGISTER_LAST_BIT; index >= 0 && carry; index--) {
        int sum = negatedSecond.getBit(index) + carry;
        negatedSecond.setBit(index, sum % 2);
        carry = sum / 2;
    }
    return addTwosComplement(first, negatedSecond);
}

// Задание 4: Умножение двух чисел в прямом коде
BinaryRegister BinaryOperations::multiplySignMagnitude(
    const BinaryRegister& first,
    const BinaryRegister& second)
{
    int resultSign = computeResultSign(first, second);
    unsigned long long magnitudeFirst = readMagnitude(first);
    unsigned long long magnitudeSecond = readMagnitude(second);

    unsigned long long product = 0;
    unsigned long long multiplicand = magnitudeFirst;
    unsigned long long multiplier = magnitudeSecond;

    while (multiplier > 0) {
        if (multiplier & 1) {
            product += multiplicand;
        }
        multiplicand <<= 1;
        multiplier >>= 1;
    }

    return packSignMagnitude(resultSign, product);
}

// Задание 5: Деление двух чисел в прямом коде с точностью до 5 двоичных знаков
BinaryRegister BinaryOperations::divideSignMagnitude(
    const BinaryRegister& first,
    const BinaryRegister& second)
{
    unsigned long long magnitudeSecond = readMagnitude(second);
    if (magnitudeSecond == 0) {
        std::cerr << "Ошибка: деление на ноль!\n";
        return packSignMagnitude(0, 0);
    }

    int resultSign = computeResultSign(first, second);
    unsigned long long magnitudeFirst = readMagnitude(first);

    unsigned long long scaledDividend = magnitudeFirst << FRACTIONAL_BITS_COUNT;

    unsigned long long quotient  = 0;
    unsigned long long remainder = 0;

    const int TOTAL_QUOTIENT_BITS = REGISTER_BIT_SIZE - 1 + FRACTIONAL_BITS_COUNT;

    for (int bitIndex = TOTAL_QUOTIENT_BITS - 1; bitIndex >= 0; bitIndex--) {
        remainder = (remainder << 1) | ((scaledDividend >> bitIndex) & 1);

        if (remainder >= magnitudeSecond) {
            remainder -= magnitudeSecond;
            quotient |= (1ULL << bitIndex);
        }
    }
    return packSignMagnitude(resultSign, quotient);
}
}