#include <iostream>
#include "convert_binary.h"
#include "binary_operations.h"
#include "float_operation.h"
#include "bcd_5421.h"
#include <windows.h>

static const int BINARY_REGISTER_SIZE  = 32;
static const int IEEE754_SIGN_SEPARATOR = 0;
static const int IEEE754_EXP_SEPARATOR  = 8;
static const int DIVISION_INT_BIT_START  = 1;
static const int DIVISION_INT_BIT_END = 26;
static const int DIVISION_FRAC_BIT_START = 27;
static const int DIVISION_FRAC_BIT_END  = 31;
static const int DIVISION_FRAC_DENOMINATOR = 32;
static void printBinaryRegister(const Binary::BinaryRegister& reg) {
    for (int bitIndex = 0; bitIndex < BINARY_REGISTER_SIZE; ++bitIndex) {
        std::cout << reg.getBit(bitIndex);
    }
    std::cout << "\n";
}

static void printDivisionResult(const Binary::BinaryRegister& reg) {
    std::cout << reg.getBit(0);
    for (int bitIndex = DIVISION_INT_BIT_START; bitIndex <= DIVISION_INT_BIT_END; ++bitIndex) {
        std::cout << reg.getBit(bitIndex);
    }
    std::cout << ",";
    for (int bitIndex = DIVISION_FRAC_BIT_START; bitIndex <= DIVISION_FRAC_BIT_END; ++bitIndex) {
        std::cout << reg.getBit(bitIndex);
    }
    std::cout << "\n";
}

static void printIeeeBits(const FloatOps::FloatBits& floatBits) {
    for (int bitIndex = 0; bitIndex < BINARY_REGISTER_SIZE; ++bitIndex) {
        std::cout << floatBits.getBit(bitIndex);
        if (bitIndex == IEEE754_SIGN_SEPARATOR || bitIndex == IEEE754_EXP_SEPARATOR) {
            std::cout << " ";
        }
    }
}

static void printBcdNumber(const BCD5421::BCDNumber& bcdNumber) {
    for (int digitIndex = 0; digitIndex < bcdNumber.getLength(); ++digitIndex) {
        for (int bitPos = 3; bitPos >= 0; --bitPos) {
            std::cout << ((bcdNumber.getDigit(digitIndex) >> bitPos) & 1);
        }
        if (digitIndex < bcdNumber.getLength() - 1) {
            std::cout << " ";
        }
    }
}

// задание 1: представление чисел

static void showNumberRepresentations(int number) {
    Binary::BinaryRegister binaryReg;

    binaryReg.setSignMagnitude(number);
    std::cout << "Прямой код:          ";
    printBinaryRegister(binaryReg);
    std::cout << "  проверка (10): " << binaryReg.signMagnitudeToDecimal() << "\n";

    binaryReg.setOnesComplement(number);
    std::cout << "Обратный код:        ";
    printBinaryRegister(binaryReg);
    std::cout << "  проверка (10): " << binaryReg.onesComplementToDecimal() << "\n";

    binaryReg.setTwosComplement(number);
    std::cout << "Дополнительный код:  ";
    printBinaryRegister(binaryReg);
    std::cout << "  проверка (10): " << binaryReg.twosComplementToDecimal() << "\n";
}

// задание 2–5

static void showTwosComplementArithmetic(int firstNumber, int secondNumber) {
    Binary::BinaryRegister firstTwos, secondTwos;
    firstTwos.setTwosComplement(firstNumber);
    secondTwos.setTwosComplement(secondNumber);

    std::cout << "\nСложение в дополнительном коде\n";
    Binary::BinaryRegister addResult =
        Binary::BinaryOperations::addTwosComplement(firstTwos, secondTwos);
    std::cout << firstNumber << " + " << secondNumber << " = ";
    printBinaryRegister(addResult);
    std::cout << "  проверка (10): " << addResult.twosComplementToDecimal() << "\n";

    std::cout << "\nВычитание в дополнительном коде\n";
    Binary::BinaryRegister subResult =
        Binary::BinaryOperations::subtractTwosComplement(firstTwos, secondTwos);
    std::cout << firstNumber << " - " << secondNumber << " = ";
    printBinaryRegister(subResult);
    std::cout << "  проверка (10): " << subResult.twosComplementToDecimal() << "\n";
}

static void showSignMagnitudeArithmetic(int firstNumber, int secondNumber) {
    Binary::BinaryRegister firstSign, secondSign;
    firstSign.setSignMagnitude(firstNumber);
    secondSign.setSignMagnitude(secondNumber);

    std::cout << "\nУмножение в прямом коде\n";
    Binary::BinaryRegister mulResult =
        Binary::BinaryOperations::multiplySignMagnitude(firstSign, secondSign);
    std::cout << firstNumber << " * " << secondNumber << " = ";
    printBinaryRegister(mulResult);
    std::cout << "  проверка (10): " << mulResult.signMagnitudeToDecimal() << "\n";

    std::cout << "\nДеление в прямом коде\n";
    Binary::BinaryRegister divResult =
        Binary::BinaryOperations::divideSignMagnitude(firstSign, secondSign);
    std::cout << firstNumber << " / " << secondNumber << " = ";
    printDivisionResult(divResult);
    int signBit        = divResult.getBit(0);
    int integerPart    = 0;
    for (int bitIndex = DIVISION_INT_BIT_START; bitIndex <= DIVISION_INT_BIT_END; ++bitIndex) {
        integerPart = integerPart * 2 + divResult.getBit(bitIndex);
    }
    int fractionalPart = 0;
    for (int bitIndex = DIVISION_FRAC_BIT_START; bitIndex <= DIVISION_FRAC_BIT_END; ++bitIndex) {
        fractionalPart = fractionalPart * 2 + divResult.getBit(bitIndex);
    }
    double decimalResult = integerPart + fractionalPart / static_cast<double>(DIVISION_FRAC_DENOMINATOR);
    if (signBit) decimalResult = -decimalResult;
    std::cout << "  проверка (10): " << decimalResult << "\n";
}

// задание 6: IEEE-754

static void showIeeeRepresentation(float number, const FloatOps::FloatBits& floatBits) {
    std::cout << "\nЧисло " << number << ":\n";
    std::cout << "Битовое представление: ";
    printIeeeBits(floatBits);
    std::cout << " (знак|порядок|мантисса)\n";
    std::cout << "Знак: "      << floatBits.getSign()
              << ", Порядок: " << floatBits.getExponent()
              << ", Мантисса: " << floatBits.getMantissa() << "\n";
    std::cout << "  проверка (10): " << FloatOps::bitsToFloat(floatBits) << "\n";
}

static void showIeeeOperation(const char* operationName,
                               const char* operationSymbol,
                               float firstOperand,
                               float secondOperand,
                               const FloatOps::FloatBits& operationResult) {
    float decimalResult = FloatOps::bitsToFloat(operationResult);
    std::cout << "\n" << operationName << " в формате IEEE-754\n";
    std::cout << firstOperand << " " << operationSymbol << " "
              << secondOperand << " = " << decimalResult << "\n";
    std::cout << "Результат в двоичном: ";
    printIeeeBits(operationResult);
    std::cout << "\n";
}

static void showIeeeArithmetic(float firstNumber, float secondNumber) {
    FloatOps::FloatBits firstBits  = FloatOps::floatToBits(firstNumber);
    FloatOps::FloatBits secondBits = FloatOps::floatToBits(secondNumber);

    std::cout << "\nПредставление в формате IEEE-754 (32 бита):\n";
    showIeeeRepresentation(firstNumber,  firstBits);
    showIeeeRepresentation(secondNumber, secondBits);

    showIeeeOperation("Сложение",  "+", firstNumber, secondNumber,
                      FloatOps::addFloat(firstBits, secondBits));
    showIeeeOperation("Вычитание", "-", firstNumber, secondNumber,
                      FloatOps::subFloat(firstBits, secondBits));
    showIeeeOperation("Умножение", "*", firstNumber, secondNumber,
                      FloatOps::mulFloat(firstBits, secondBits));
    showIeeeOperation("Деление",   "/", firstNumber, secondNumber,
                      FloatOps::divFloat(firstBits, secondBits));
}

// задание 7: BCD 5421

static void showBcdRepresentation(int number) {
    BCD5421::BCDNumber bcdNumber = BCD5421::decimalToBCD5421(number);
    std::cout << "\nЧисло " << number << ":\n";
    std::cout << "Код 5421: ";
    printBcdNumber(bcdNumber);
    std::cout << "\n";
    std::cout << "  проверка (10): " << BCD5421::bcd5421ToDecimal(bcdNumber) << "\n";
}

static void showBcdArithmetic(int firstNumber, int secondNumber) {
    BCD5421::BCDNumber firstBcd  = BCD5421::decimalToBCD5421(firstNumber);
    BCD5421::BCDNumber secondBcd = BCD5421::decimalToBCD5421(secondNumber);

    std::cout << "\nПредставление в коде 5421:\n";
    showBcdRepresentation(firstNumber);
    showBcdRepresentation(secondNumber);

    BCD5421::BCDNumber addResult = BCD5421::addBCD5421(firstBcd, secondBcd);
    int decimalSum = BCD5421::bcd5421ToDecimal(addResult);

    std::cout << "\nСложение в коде 5421\n";
    std::cout << firstNumber << " + " << secondNumber << " = " << decimalSum << "\n";
    std::cout << "Результат в коде 5421: ";
    printBcdNumber(addResult);
    std::cout << "\n";
    std::cout << "  проверка (10): " << decimalSum << "\n";
}

static int readInteger(const char* prompt) {
    int value;
    std::cout << prompt;
    std::cin >> value;
    return value;
}

static float readFloat(const char* prompt) {
    float value;
    std::cout << prompt;
    std::cin >> value;
    return value;
}

static int readNonNegativeInteger(const char* prompt) {
    int value;
    std::cout << prompt;
    std::cin >> value;
    while (value < 0) {
        std::cout << "Ошибка: введите неотрицательное число: ";
        std::cin >> value;
    }
    return value;
}

int main() {
    SetConsoleOutputCP(1251);
    SetConsoleCP(1251);
    setlocale(LC_ALL, "Russian");

    std::cout << "\n Задания 1-5 \n";
    int firstInt  = readInteger("Введите первое число: ");
    int secondInt = readInteger("Введите второе число: ");

    std::cout << "\nПредставление чисел\n";
    std::cout << "\nЧисло " << firstInt << ":\n";
    showNumberRepresentations(firstInt);
    std::cout << "\nЧисло " << secondInt << ":\n";
    showNumberRepresentations(secondInt);

    showTwosComplementArithmetic(firstInt, secondInt);
    showSignMagnitudeArithmetic(firstInt, secondInt);

    std::cout << "\n Задание 6 \n";
    float firstFloat  = readFloat("\nВведите первое вещественное число: ");
    float secondFloat = readFloat("Введите второе вещественное число: ");
    showIeeeArithmetic(firstFloat, secondFloat);

    std::cout << "\n Задание 7 \n";
    int firstBcd  = readNonNegativeInteger("\nВведите первое число для кода 5421 (только неотрицательное): ");
    int secondBcd = readNonNegativeInteger("Введите второе число для кода 5421 (только неотрицательное): ");
    showBcdArithmetic(firstBcd, secondBcd);

    return 0;
}
