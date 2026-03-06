#include "float_operation.h"

namespace FloatOps {

static const int MANTISSA_PRODUCT_HIGH_BIT = 47;
static const int DIVISION_SCALE_SHIFT  = 23;

int FloatBits::getBit(int index) const {
    if (index >= 0 && index < TOTAL_BITS) return bits[index];
    return 0;
}

int FloatBits::getSign() const {
    return bits[SIGN_BIT_POS];
}

int FloatBits::getExponent() const {
    int exponent = 0;
    for (int index = EXPONENT_START; index <= EXPONENT_END; index++) {
        exponent = (exponent << 1) | bits[index];
    }
    return exponent;
}

unsigned int FloatBits::getMantissa() const {
    unsigned int mantissa = 0;
    for (int index = MANTISSA_START; index < TOTAL_BITS; index++) {
        mantissa = (mantissa << 1) | static_cast<unsigned int>(bits[index]);
    }
    return mantissa;
}

static float applyPowerOfTwo(float value, int exponent) {
    if (exponent >= 0) {
        for (int count = 0; count < exponent;  count++) value *= 2.0f;
    } else {
        for (int count = 0; count < -exponent; count++) value /= 2.0f;
    }
    return value;
}

static FloatBits packFloat(int sign, int biasedExponent, unsigned long long mantissa) {
    FloatBits result;
    result.bits[FloatBits::SIGN_BIT_POS] = sign;
    for (int index = FloatBits::EXPONENT_BITS - 1; index >= 0; index--) {
        result.bits[FloatBits::EXPONENT_END - index] = (biasedExponent >> index) & 1;
    }
    for (int index = FloatBits::MANTISSA_BITS - 1; index >= 0; index--) {
        result.bits[FloatBits::MANTISSA_END - index] = static_cast<int>((mantissa >> index) & 1);
    }
    return result;
}

static int extractExponent(const FloatBits& fb) {
    int exponent = 0;
    for (int index = FloatBits::EXPONENT_START; index <= FloatBits::EXPONENT_END; index++) {
        exponent = (exponent << 1) | fb.bits[index];
    }
    return exponent;
}

static unsigned long long extractMantissa(const FloatBits& fb) {
    unsigned long long mantissa = 0;
    for (int index = FloatBits::MANTISSA_START; index < FloatBits::TOTAL_BITS; index++) {
        mantissa = (mantissa << 1) | static_cast<unsigned long long>(fb.bits[index]);
    }
    return mantissa;
}

static unsigned long long restoreHiddenBit(unsigned long long mantissa, int exponent) {
    if (exponent != 0) {
        mantissa |= (1ULL << FloatBits::HIDDEN_BIT_POS);
    }
    return mantissa;
}

static void normalizeMantissa(unsigned long long& mantissa, int& exponent) {
    if (mantissa & (1ULL << (FloatBits::HIDDEN_BIT_POS + 1))) {
        mantissa >>= 1;
        exponent++;
    } else {
        while (mantissa != 0 && (mantissa & (1ULL << FloatBits::HIDDEN_BIT_POS)) == 0) {
            mantissa <<= 1;
            exponent--;
        }
    }
}

static unsigned long long removeHiddenBit(unsigned long long mantissa) {
    return mantissa & ~(1ULL << FloatBits::HIDDEN_BIT_POS);
}

static int clampExponent(int exponent) {
    if (exponent >= FloatBits::INFINITY_EXPONENT) return FloatBits::INFINITY_EXPONENT - 1;
    if (exponent <= 0) return 1;
    return exponent;
}

static int integerToBits(int integerPart, int* bitsArray) {
    if (integerPart == 0) {
        bitsArray[0] = 0;
        return 1;
    }
    int length = 0;
    while (integerPart > 0) {
        bitsArray[length++] = integerPart % 2;
        integerPart /= 2;
    }
    for (int left = 0, right = length - 1; left < right; left++, right--) {
        int temp = bitsArray[left];
        bitsArray[left]  = bitsArray[right];
        bitsArray[right] = temp;
    }
    return length;
}

static void fractionalToBits(float fractionalPart, int* bitsArray, int length) {
    for (int index = 0; index < length; index++) {
        fractionalPart *= 2.0f;
        if (fractionalPart >= 1.0f) {
            bitsArray[index] = 1;
            fractionalPart  -= 1.0f;
        } else {
            bitsArray[index] = 0;
        }
    }
}

static void buildMantissaAndExponent(
    const int* intBits, int intLength,
    const int* fracBits,
    int* mantissa, int& exponent)
{
    if (intBits[0] == 0 && intLength == 1) {
        int firstOne = -1;
        for (int index = 0; index < FloatBits::MANTISSA_BITS; index++) {
            if (fracBits[index] == 1) { firstOne = index; break; }
        }
        if (firstOne == -1) { exponent = 0; return; }
        exponent = -(firstOne + 1);
        for (int index = 0; index < FloatBits::MANTISSA_BITS - firstOne - 1; index++) {
            mantissa[index] = fracBits[index + firstOne + 1];
        }
    } else {
        exponent = intLength - 1;
        for (int index = 1; index < intLength; index++) {
            mantissa[index - 1] = intBits[index];
        }
        for (int index = 0; index < FloatBits::MANTISSA_BITS - (intLength - 1); index++) {
            mantissa[intLength - 1 + index] = fracBits[index];
        }
    }
}

// Задание 6: Перевод float в битовый массив IEEE-754 (32 бита)
FloatBits floatToBits(float value) {
    FloatBits result;
    if (value == 0.0f) return result;

    result.bits[FloatBits::SIGN_BIT_POS] = (value < 0.0f) ? 1 : 0;
    if (value < 0.0f) value = -value;

    int integerPart = static_cast<int>(value);
    float fracPart = value - static_cast<float>(integerPart);

    int intBits[32] = {0};
    int fracBits[FloatBits::MANTISSA_BITS] = {0};
    int mantissa[FloatBits::MANTISSA_BITS] = {0};
    int exponent = 0;

    int intLength = integerToBits(integerPart, intBits);
    fractionalToBits(fracPart, fracBits, FloatBits::MANTISSA_BITS);
    buildMantissaAndExponent(intBits, intLength, fracBits, mantissa, exponent);

    int biasedExponent = exponent + FloatBits::EXPONENT_BIAS;
    for (int index = FloatBits::EXPONENT_BITS - 1; index >= 0; index--) {
        result.bits[FloatBits::EXPONENT_END - index] = (biasedExponent >> index) & 1;
    }
    for (int index = 0; index < FloatBits::MANTISSA_BITS; index++) {
        result.bits[FloatBits::MANTISSA_START + index] = mantissa[index];
    }
    return result;
}

// Задание 6: Обратный перевод — битовый массив IEEE-754 -> float
float bitsToFloat(FloatBits fb) {
    int sign  = fb.bits[FloatBits::SIGN_BIT_POS];
    int exponent = fb.getExponent();
    unsigned int mantissa = fb.getMantissa();

    if (exponent == 0 && mantissa == 0) return sign ? -0.0f : 0.0f;

    float reconstructed = 1.0f;
    float bitWeight  = 0.5f;
    for (int index = FloatBits::MANTISSA_START; index < FloatBits::TOTAL_BITS; index++) {
        if (fb.bits[index]) reconstructed += bitWeight;
        bitWeight /= 2.0f;
    }

    int realExponent = exponent - FloatBits::EXPONENT_BIAS;
    reconstructed  = applyPowerOfTwo(reconstructed, realExponent);

    return sign ? -reconstructed : reconstructed;
}

// Задание 6: Сложение двух чисел в формате IEEE-754
FloatBits addFloat(FloatBits first, FloatBits second) {
    int signFirst = first.bits[FloatBits::SIGN_BIT_POS];
    int signSecond  = second.bits[FloatBits::SIGN_BIT_POS];
    int exponentFirst  = extractExponent(first);
    int exponentSecond = extractExponent(second);

    unsigned long long mantissaFirst  = restoreHiddenBit(extractMantissa(first),  exponentFirst);
    unsigned long long mantissaSecond = restoreHiddenBit(extractMantissa(second), exponentSecond);

    if (exponentFirst > exponentSecond) {
        mantissaSecond >>= (exponentFirst - exponentSecond);
        exponentSecond  = exponentFirst;
    } else if (exponentSecond > exponentFirst) {
        mantissaFirst  >>= (exponentSecond - exponentFirst);
        exponentFirst = exponentSecond;
    }

    unsigned long long resultMantissa;
    int resultSign;
    if (signFirst == signSecond) {
        resultMantissa = mantissaFirst + mantissaSecond;
        resultSign = signFirst;
    } else if (mantissaFirst >= mantissaSecond) {
        resultMantissa = mantissaFirst - mantissaSecond;
        resultSign  = signFirst;
    } else {
        resultMantissa = mantissaSecond - mantissaFirst;
        resultSign = signSecond;
    }

    if (resultMantissa == 0) return packFloat(0, 0, 0);

    int resultExponent = exponentFirst;
    normalizeMantissa(resultMantissa, resultExponent);
    resultMantissa = removeHiddenBit(resultMantissa);
    resultExponent = clampExponent(resultExponent);
    return packFloat(resultSign, resultExponent, resultMantissa);
}

// Задание 6: Вычитание в формате IEEE-754
FloatBits subFloat(FloatBits first, FloatBits second) {
    second.bits[FloatBits::SIGN_BIT_POS] = 1 - second.bits[FloatBits::SIGN_BIT_POS];
    return addFloat(first, second);
}

// Задание 6: Умножение двух чисел в формате IEEE-754
FloatBits mulFloat(FloatBits first, FloatBits second) {
    int resultSign  = first.bits[FloatBits::SIGN_BIT_POS] ^ second.bits[FloatBits::SIGN_BIT_POS];
    int exponentFirst  = extractExponent(first);
    int exponentSecond = extractExponent(second);

    unsigned long long mantissaFirst  = restoreHiddenBit(extractMantissa(first),  exponentFirst);
    unsigned long long mantissaSecond = restoreHiddenBit(extractMantissa(second), exponentSecond);

    unsigned long long resultMantissa = mantissaFirst * mantissaSecond;

    int resultExponent = (exponentFirst == 0 || exponentSecond == 0)
        ? 0
        : exponentFirst + exponentSecond - FloatBits::EXPONENT_BIAS;

    if (resultMantissa & (1ULL << MANTISSA_PRODUCT_HIGH_BIT)) {
        resultMantissa >>= (DIVISION_SCALE_SHIFT + 1);
        resultExponent++;
    } else {
        resultMantissa >>= DIVISION_SCALE_SHIFT;
    }
    while (resultMantissa != 0 && (resultMantissa & (1ULL << FloatBits::HIDDEN_BIT_POS)) == 0) {
        resultMantissa <<= 1;
        resultExponent--;
    }

    resultMantissa = removeHiddenBit(resultMantissa);
    resultExponent = clampExponent(resultExponent);
    return packFloat(resultSign, resultExponent, resultMantissa);
}

// Задание 6: Деление двух чисел в формате IEEE-754
FloatBits divFloat(FloatBits first, FloatBits second) {
    int exponentSecond  = extractExponent(second);
    unsigned long long rawMantissaSecond = extractMantissa(second);
    if (exponentSecond == 0 && rawMantissaSecond == 0) return packFloat(0, 0, 0);

    unsigned long long mantissaSecond = restoreHiddenBit(rawMantissaSecond, exponentSecond);

    int resultSign = first.bits[FloatBits::SIGN_BIT_POS] ^ second.bits[FloatBits::SIGN_BIT_POS];
    int exponentFirst = extractExponent(first);

    unsigned long long mantissaFirst = restoreHiddenBit(extractMantissa(first), exponentFirst);
    if (exponentSecond == 0) exponentSecond = 1;

    unsigned long long resultMantissa = (mantissaFirst << DIVISION_SCALE_SHIFT) / mantissaSecond;

    int resultExponent = exponentFirst - exponentSecond + FloatBits::EXPONENT_BIAS;

    normalizeMantissa(resultMantissa, resultExponent);
    resultMantissa = removeHiddenBit(resultMantissa);
    resultExponent = clampExponent(resultExponent);
    return packFloat(resultSign, resultExponent, resultMantissa);
}

}