#include <gtest/gtest.h>
#include "convert_binary.h"
#include "binary_operations.h"
#include "float_operation.h"
#include "bcd_5421.h"

TEST(ConvertBinaryTest, SignMagnitude_Positive) {
    Binary::BinaryRegister reg;
    reg.setSignMagnitude(42);
    EXPECT_EQ(reg.getBit(0), 0);
    EXPECT_EQ(reg.signMagnitudeToDecimal(), 42);
}

TEST(ConvertBinaryTest, SignMagnitude_Negative) {
    Binary::BinaryRegister reg;
    reg.setSignMagnitude(-42);
    EXPECT_EQ(reg.getBit(0), 1);
    EXPECT_EQ(reg.signMagnitudeToDecimal(), -42);
}

TEST(ConvertBinaryTest, SignMagnitude_ZeroAndBounds) {
    Binary::BinaryRegister reg;
    reg.setSignMagnitude(0);
    EXPECT_EQ(reg.signMagnitudeToDecimal(), 0);
    EXPECT_EQ(reg.getBit(-1), 0);
    EXPECT_EQ(reg.getBit(32), 0);
    reg.setBit(-1, 1);
    reg.setBit(32, 1);
    EXPECT_EQ(reg.signMagnitudeToDecimal(), 0);
}

TEST(ConvertBinaryTest, OnesComplement_Positive) {
    Binary::BinaryRegister reg;
    reg.setOnesComplement(17);
    EXPECT_EQ(reg.getBit(0), 0);
    EXPECT_EQ(reg.onesComplementToDecimal(), 17);
}

TEST(ConvertBinaryTest, OnesComplement_Negative) {
    Binary::BinaryRegister reg;
    reg.setOnesComplement(-17);
    EXPECT_EQ(reg.getBit(0), 1);
    EXPECT_EQ(reg.onesComplementToDecimal(), -17);
}

TEST(ConvertBinaryTest, TwosComplement_Positive) {
    Binary::BinaryRegister reg;
    reg.setTwosComplement(25);
    EXPECT_EQ(reg.getBit(0), 0);
    EXPECT_EQ(reg.twosComplementToDecimal(), 25);
}

TEST(ConvertBinaryTest, TwosComplement_Negative) {
    Binary::BinaryRegister reg;
    reg.setTwosComplement(-25);
    EXPECT_EQ(reg.getBit(0), 1);
    EXPECT_EQ(reg.twosComplementToDecimal(), -25);
}

TEST(ConvertBinaryTest, TwosComplement_MinusOne_AllBitsSet) {
    Binary::BinaryRegister reg;
    reg.setTwosComplement(-1);
    for (int index = 0; index < 32; index++) {
        EXPECT_EQ(reg.getBit(index), 1);
    }
    EXPECT_EQ(reg.twosComplementToDecimal(), -1);
}

TEST(BinaryOpsTest, AddTwosComplement_BothPositive) {
    Binary::BinaryRegister first, second;
    first.setTwosComplement(100);
    second.setTwosComplement(200);
    Binary::BinaryRegister result = Binary::BinaryOperations::addTwosComplement(first, second);
    EXPECT_EQ(result.twosComplementToDecimal(), 300);
}

TEST(BinaryOpsTest, AddTwosComplement_NegativeResult) {
    Binary::BinaryRegister first, second;
    first.setTwosComplement(-50);
    second.setTwosComplement(-30);
    Binary::BinaryRegister result = Binary::BinaryOperations::addTwosComplement(first, second);
    EXPECT_EQ(result.twosComplementToDecimal(), -80);
}

TEST(BinaryOpsTest, SubtractTwosComplement_PositiveResult) {
    Binary::BinaryRegister first, second;
    first.setTwosComplement(50);
    second.setTwosComplement(30);
    Binary::BinaryRegister result = Binary::BinaryOperations::subtractTwosComplement(first, second);
    EXPECT_EQ(result.twosComplementToDecimal(), 20);
}

TEST(BinaryOpsTest, SubtractTwosComplement_NegativeResult) {
    Binary::BinaryRegister first, second;
    first.setTwosComplement(10);
    second.setTwosComplement(40);
    Binary::BinaryRegister result = Binary::BinaryOperations::subtractTwosComplement(first, second);
    EXPECT_EQ(result.twosComplementToDecimal(), -30);
}

TEST(BinaryOpsTest, Multiply_BothPositive) {
    Binary::BinaryRegister first, second;
    first.setSignMagnitude(7);
    second.setSignMagnitude(8);
    Binary::BinaryRegister result = Binary::BinaryOperations::multiplySignMagnitude(first, second);
    EXPECT_EQ(result.signMagnitudeToDecimal(), 56);
}

TEST(BinaryOpsTest, Multiply_DifferentSigns) {
    Binary::BinaryRegister first, second;
    first.setSignMagnitude(-6);
    second.setSignMagnitude(9);
    Binary::BinaryRegister result = Binary::BinaryOperations::multiplySignMagnitude(first, second);
    EXPECT_EQ(result.signMagnitudeToDecimal(), -54);
}

TEST(BinaryOpsTest, Multiply_BothNegative) {
    Binary::BinaryRegister first, second;
    first.setSignMagnitude(-5);
    second.setSignMagnitude(-4);
    Binary::BinaryRegister result = Binary::BinaryOperations::multiplySignMagnitude(first, second);
    EXPECT_EQ(result.signMagnitudeToDecimal(), 20);
}

TEST(BinaryOpsTest, Divide_ExactResult) {
    Binary::BinaryRegister first, second;
    first.setSignMagnitude(20);
    second.setSignMagnitude(4);
    Binary::BinaryRegister result = Binary::BinaryOperations::divideSignMagnitude(first, second);
    int integerPart = 0;
    for (int index = 1; index <= 26; index++) integerPart = integerPart * 2 + result.getBit(index);
    int fractionalPart = 0;
    for (int index = 27; index <= 31; index++) fractionalPart = fractionalPart * 2 + result.getBit(index);
    EXPECT_EQ(result.getBit(0), 0);
    EXPECT_NEAR(integerPart + fractionalPart / 32.0, 5.0, 1e-6);
}

TEST(BinaryOpsTest, Divide_FractionalResult_NegativeSign) {
    Binary::BinaryRegister first, second;
    first.setSignMagnitude(5);
    second.setSignMagnitude(-2);
    Binary::BinaryRegister result = Binary::BinaryOperations::divideSignMagnitude(first, second);
    int integerPart = 0;
    for (int index = 1; index <= 26; index++) integerPart = integerPart * 2 + result.getBit(index);
    int fractionalPart = 0;
    for (int index = 27; index <= 31; index++) fractionalPart = fractionalPart * 2 + result.getBit(index);
    double decimal = integerPart + fractionalPart / 32.0;
    EXPECT_EQ(result.getBit(0), 1);
    EXPECT_NEAR(decimal, 2.5, 0.1);
}

TEST(BinaryOpsTest, Divide_ByZero_ReturnsZero) {
    Binary::BinaryRegister first, second;
    first.setSignMagnitude(10);
    second.setSignMagnitude(0);
    Binary::BinaryRegister result = Binary::BinaryOperations::divideSignMagnitude(first, second);
    EXPECT_EQ(result.signMagnitudeToDecimal(), 0);
}

TEST(FloatOpsTest, FloatToBitsAndBack_Positive) {
    FloatOps::FloatBits fb = FloatOps::floatToBits(5.25f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(fb), 5.25f);
}

TEST(FloatOpsTest, FloatToBitsAndBack_Negative) {
    FloatOps::FloatBits fb = FloatOps::floatToBits(-3.75f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(fb), -3.75f);
}

TEST(FloatOpsTest, FloatToBitsAndBack_FractionLessThanOne) {
    FloatOps::FloatBits fb = FloatOps::floatToBits(0.25f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(fb), 0.25f);
}

TEST(FloatOpsTest, BitsToFloat_Zero) {
    FloatOps::FloatBits fb = FloatOps::floatToBits(0.0f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(fb), 0.0f);
}

TEST(FloatOpsTest, AddFloat_SameSigns) {
    FloatOps::FloatBits first  = FloatOps::floatToBits(1.5f);
    FloatOps::FloatBits second = FloatOps::floatToBits(2.5f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(FloatOps::addFloat(first, second)), 4.0f);
}

TEST(FloatOpsTest, AddFloat_DifferentSigns_PositiveResult) {
    FloatOps::FloatBits first  = FloatOps::floatToBits(5.25f);
    FloatOps::FloatBits second = FloatOps::floatToBits(-3.75f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(FloatOps::addFloat(first, second)), 1.5f);
}

TEST(FloatOpsTest, AddFloat_DifferentSigns_NegativeResult) {
    FloatOps::FloatBits first  = FloatOps::floatToBits(3.75f);
    FloatOps::FloatBits second = FloatOps::floatToBits(-5.25f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(FloatOps::addFloat(first, second)), -1.5f);
}

TEST(FloatOpsTest, SubFloat) {
    FloatOps::FloatBits first  = FloatOps::floatToBits(10.0f);
    FloatOps::FloatBits second = FloatOps::floatToBits(3.5f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(FloatOps::subFloat(first, second)), 6.5f);
}

TEST(FloatOpsTest, MulFloat_Positive) {
    FloatOps::FloatBits first  = FloatOps::floatToBits(2.5f);
    FloatOps::FloatBits second = FloatOps::floatToBits(4.0f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(FloatOps::mulFloat(first, second)), 10.0f);
}

TEST(FloatOpsTest, MulFloat_NegativeResult) {
    FloatOps::FloatBits first  = FloatOps::floatToBits(-3.0f);
    FloatOps::FloatBits second = FloatOps::floatToBits(2.5f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(FloatOps::mulFloat(first, second)), -7.5f);
}

TEST(FloatOpsTest, DivFloat_ExactResult) {
    FloatOps::FloatBits first  = FloatOps::floatToBits(7.5f);
    FloatOps::FloatBits second = FloatOps::floatToBits(2.5f);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(FloatOps::divFloat(first, second)), 3.0f);
}

TEST(FloatOpsTest, DivFloat_ByZero_ReturnsZero) {
    FloatOps::FloatBits first  = FloatOps::floatToBits(5.0f);
    FloatOps::FloatBits second = FloatOps::floatToBits(0.0f);
    FloatOps::FloatBits result = FloatOps::divFloat(first, second);
    EXPECT_FLOAT_EQ(FloatOps::bitsToFloat(result), 0.0f);
}

TEST(BcdTest, AllDigits_RoundTrip) {
    for (int digit = 0; digit <= 9; digit++) {
        BCD5421::BCDNumber bcd = BCD5421::decimalToBCD5421(digit);
        EXPECT_EQ(BCD5421::bcd5421ToDecimal(bcd), digit);
    }
}

TEST(BcdTest, MultiDigit_RoundTrip) {
    BCD5421::BCDNumber bcd = BCD5421::decimalToBCD5421(5678);
    EXPECT_EQ(BCD5421::bcd5421ToDecimal(bcd), 5678);
    EXPECT_EQ(bcd.getLength(), 4);
}

TEST(BcdTest, Add_NoCarry) {
    BCD5421::BCDNumber first  = BCD5421::decimalToBCD5421(23);
    BCD5421::BCDNumber second = BCD5421::decimalToBCD5421(14);
    EXPECT_EQ(BCD5421::bcd5421ToDecimal(BCD5421::addBCD5421(first, second)), 37);
}

TEST(BcdTest, Add_WithCarry) {
    BCD5421::BCDNumber first  = BCD5421::decimalToBCD5421(78);
    BCD5421::BCDNumber second = BCD5421::decimalToBCD5421(45);
    EXPECT_EQ(BCD5421::bcd5421ToDecimal(BCD5421::addBCD5421(first, second)), 123);
}

TEST(BcdTest, Add_CarryCreatesNewDigit) {
    BCD5421::BCDNumber first  = BCD5421::decimalToBCD5421(999);
    BCD5421::BCDNumber second = BCD5421::decimalToBCD5421(1);
    BCD5421::BCDNumber result = BCD5421::addBCD5421(first, second);
    EXPECT_EQ(BCD5421::bcd5421ToDecimal(result), 1000);
    EXPECT_EQ(result.getLength(), 4);
}