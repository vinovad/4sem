#include "convert_binary.h"

namespace Binary {

BinaryRegister::BinaryRegister() {
    clear();
}

void BinaryRegister::clear() {
    for (int index = 0; index < BIT_SIZE; index++) {
        bits[index] = 0;
    }
}

int BinaryRegister::getBit(int index) const {
    if (index >= 0 && index < BIT_SIZE) {
        return bits[index];
    }
    return 0;
}

void BinaryRegister::setBit(int index, int value) {
    if (index >= 0 && index < BIT_SIZE) {
        bits[index] = value;
    }
}

void BinaryRegister::print() const {
    for (int index = 0; index < BIT_SIZE; index++) {
        std::cout << bits[index];
    }
    std::cout << std::endl;
}

static void writeMagnitude(int absoluteValue, int* bits, int lastBit, int firstMagnitudeBit) {
    for (int index = lastBit; index >= firstMagnitudeBit; index--) {
        bits[index] = absoluteValue % 2;
        absoluteValue /= 2;
    }
}

// «адание 1: пр€мой код
void BinaryRegister::setSignMagnitude(int number) {
    clear();
    if (number < 0) {
        bits[SIGN_BIT_POSITION] = 1;
        number = -number;
    }
    writeMagnitude(number, bits, LAST_BIT_INDEX, FIRST_MAGNITUDE_BIT);
}

void BinaryRegister::invertMagnitudeBits() {
    for (int index = FIRST_MAGNITUDE_BIT; index < BIT_SIZE; index++) {
        bits[index] = 1 - bits[index];
    }
}

// «адание 2: обратный коде
void BinaryRegister::setOnesComplement(int number) {
    setSignMagnitude(number);
    if (number < 0) {
        invertMagnitudeBits();
    }
}

void BinaryRegister::addOneToMagnitude() {
    int carry = 1;
    for (int index = LAST_BIT_INDEX; index >= FIRST_MAGNITUDE_BIT && carry; index--) {
        int sum    = bits[index] + carry;
        bits[index] = sum % 2;
        carry      = sum / 2;
    }
}

// «адание 3: дополнительный код
void BinaryRegister::setTwosComplement(int number) {
    setOnesComplement(number);
    if (number < 0) {
        addOneToMagnitude();
    }
}

int BinaryRegister::readMagnitudeAsInt() const {
    int value = 0;
    for (int index = FIRST_MAGNITUDE_BIT; index < BIT_SIZE; index++) {
        value = value * 2 + bits[index];
    }
    return value;
}

// «адание 8: декодирование пр€мого кода в дес€тичное число
int BinaryRegister::signMagnitudeToDecimal() const {
    int value = readMagnitudeAsInt();
    return bits[SIGN_BIT_POSITION] ? -value : value;
}

// «адание 8: декодирование обратного кода в дес€тичное число
int BinaryRegister::onesComplementToDecimal() const {
    if (bits[SIGN_BIT_POSITION] == 0) {
        return readMagnitudeAsInt();
    }
    int value = 0;
    for (int index = FIRST_MAGNITUDE_BIT; index < BIT_SIZE; index++) {
        value = value * 2 + (1 - bits[index]);
    }
    return -value;
}

// «адание 8: декодирование дополнительного кода в дес€тичное число
int BinaryRegister::twosComplementToDecimal() const {
    if (bits[SIGN_BIT_POSITION] == 0) {
        return readMagnitudeAsInt();
    }
    int inverted[BIT_SIZE];
    for (int index = 0; index < BIT_SIZE; index++) {
        inverted[index] = 1 - bits[index];
    }
    int carry = 1;
    for (int index = LAST_BIT_INDEX; index >= 0 && carry; index--) {
        int sum = inverted[index] + carry;
        inverted[index] = sum % 2;
        carry = sum / 2;
    }
    int value = 0;
    for (int index = FIRST_MAGNITUDE_BIT; index < BIT_SIZE; index++) {
        value = value * 2 + inverted[index];
    }
    return -value;
}

}