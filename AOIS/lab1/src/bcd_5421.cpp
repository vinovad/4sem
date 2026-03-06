#include "bcd_5421.h"

namespace BCD5421 {

static const int DECIMAL_BASE = 10; 
const int DIGIT_COUNT         = 10;
const int FORBIDDEN_ZONE_LOW  = 0b0101;
const int FORBIDDEN_ZONE_HIGH = 0b0111;
const int MAX_VALID_CODE      = 0b1100; 
const int BCD_CORRECTION      = 3; // коррекция при сложении: +3 (аналог +6 в BCD8421)

static int digitToBCD5421(int digit) {
    switch (digit) {
        case 0: return 0b0000; 
        case 1: return 0b0001;
        case 2: return 0b0010; 
        case 3: return 0b0011; 
        case 4: return 0b0100; 
        case 5: return 0b1000; 
        case 6: return 0b1001; 
        case 7: return 0b1010;
        case 8: return 0b1011; 
        case 9: return 0b1100; 
        default: return 0;
    }
}

static int bcd5421ToDigit(int bcd) {
    switch (bcd) {
        case 0b0000: return 0;
        case 0b0001: return 1;
        case 0b0010: return 2;
        case 0b0011: return 3;
        case 0b0100: return 4;
        case 0b1000: return 5;
        case 0b1001: return 6;
        case 0b1010: return 7;
        case 0b1011: return 8;
        case 0b1100: return 9;
        default: return 0; 
    }
}

// Проверка: является ли 4-битный код допустимым кодом 5421
static bool isValidBCD5421(int code) {
    switch (code & 0xF) {
        case 0b0000: case 0b0001: case 0b0010: case 0b0011: case 0b0100:
        case 0b1000: case 0b1001: case 0b1010: case 0b1011: case 0b1100:
            return true;
        default:
            return false;
    }
}

static int addDigitsWithCarry(int digitA, int digitB, int carryIn, int& carryOut) {
    int codeA  = digitToBCD5421(digitA);
    int codeB  = digitToBCD5421(digitB);

    int rawSum  = codeA + codeB + carryIn;
    int carry5  = (rawSum >> 4) & 1;
    int nibble  = rawSum & 0xF; 

    int expectedDigit = (digitA + digitB + carryIn) % DECIMAL_BASE;
    int expectedCarry = (digitA + digitB + carryIn) / DECIMAL_BASE;

    bool nibbleValid   = isValidBCD5421(nibble);
    bool resultCorrect = nibbleValid  && bcd5421ToDigit(nibble) == expectedDigit  && carry5 == expectedCarry;

    if (!resultCorrect) {
        int corrected = rawSum + BCD_CORRECTION;
        carryOut = (corrected >> 4) & 1;
        return corrected & 0xF;
    }

    carryOut = carry5;
    return nibble;
}

BCDNumber decimalToBCD5421(int decimal) {
    BCDNumber result;
    result.length = 0;

    if (decimal == 0) {
        result.digits[0] = digitToBCD5421(0);
        result.length  = 1;
        return result;
    }

    int remaining = decimal;
    while (remaining > 0) {
        int digit                    = remaining % DECIMAL_BASE;
        result.digits[result.length] = digitToBCD5421(digit);
        result.length++;
        remaining /= DECIMAL_BASE;
    }

    for (int left = 0, right = result.length - 1; left < right; left++, right--) {
        int temp             = result.digits[left];
        result.digits[left]  = result.digits[right];
        result.digits[right] = temp;
    }

    return result;
}

int bcd5421ToDecimal(BCDNumber bcd) {
    int decimal = 0;
    for (int index = 0; index < bcd.length; index++) {
        decimal = decimal * DECIMAL_BASE + bcd5421ToDigit(bcd.digits[index]);
    }
    return decimal;
}

BCDNumber addBCD5421(BCDNumber first, BCDNumber second) {
    BCDNumber result;
    result.length = 0;

    int carry     = 0;
    int maxLength = first.length > second.length ? first.length : second.length;

    for (int index = 0; index < maxLength; index++) {
        int codeA = (index < first.length)
                  ? first.digits[first.length - 1 - index]
                  : digitToBCD5421(0);
        int codeB = (index < second.length)
                  ? second.digits[second.length - 1 - index]
                  : digitToBCD5421(0);

        int digitA = bcd5421ToDigit(codeA);
        int digitB = bcd5421ToDigit(codeB);
        int carryOut  = 0;
        int resultCode = addDigitsWithCarry(digitA, digitB, carry, carryOut);
        result.digits[index] = resultCode;
        result.length++;
        carry = carryOut;
    }

    if (carry == 1) {
        result.digits[result.length] = digitToBCD5421(1);
        result.length++;
    }

    for (int left = 0, right = result.length - 1; left < right; left++, right--) {
        int temp             = result.digits[left];
        result.digits[left]  = result.digits[right];
        result.digits[right] = temp;
    }

    return result;
}

}