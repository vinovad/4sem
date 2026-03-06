#ifndef FLOAT_H
#define FLOAT_H

namespace FloatOps {

    class FloatBits {
    public:
        static const int TOTAL_BITS  = 32;
        static const int SIGN_BIT_POS = 0;
        static const int EXPONENT_START = 1;
        static const int EXPONENT_END = 8;
        static const int EXPONENT_BITS = 8;
        static const int MANTISSA_BITS = 23;
        static const int MANTISSA_START = 9;
        static const int MANTISSA_END = 31;
        static const int EXPONENT_BIAS = 127;
        static const int INFINITY_EXPONENT = 255;
        static const int HIDDEN_BIT_POS = 23;

        int bits[TOTAL_BITS];

        friend FloatBits floatToBits(float value);
        friend float bitsToFloat(FloatBits fb);
        friend FloatBits addFloat(FloatBits first, FloatBits second);
        friend FloatBits subFloat(FloatBits first, FloatBits second);
        friend FloatBits mulFloat(FloatBits first, FloatBits second);
        friend FloatBits divFloat(FloatBits first, FloatBits second);

        FloatBits() {
            for (int index = 0; index < TOTAL_BITS; index++) {
                bits[index] = 0;
            }
        }

        int getBit(int index) const;
        int getSign() const;
        int getExponent() const;
        unsigned int getMantissa() const;
    };

    FloatBits floatToBits(float value);
    float bitsToFloat(FloatBits fb);
    FloatBits addFloat(FloatBits first, FloatBits second);
    FloatBits subFloat(FloatBits first, FloatBits second);
    FloatBits mulFloat(FloatBits first, FloatBits second);
    FloatBits divFloat(FloatBits first, FloatBits second);

}

#endif