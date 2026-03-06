#ifndef BINARY_H
#define BINARY_H
#include <iostream>

namespace Binary {

    class BinaryOperations;

    class BinaryRegister {
    private:
        static const int BIT_SIZE = 32;
        static const int SIGN_BIT_POSITION = 0;
        static const int FIRST_MAGNITUDE_BIT = 1;
        static const int LAST_BIT_INDEX = 31;

        int bits[BIT_SIZE];

        friend class BinaryOperations;
        void invertMagnitudeBits();
        void addOneToMagnitude();
        int  readMagnitudeAsInt() const;

    public:
        BinaryRegister();

        void clear();
        void setSignMagnitude(int number);
        void setOnesComplement(int number);
        void setTwosComplement(int number);

        int signMagnitudeToDecimal()  const;
        int onesComplementToDecimal() const;
        int twosComplementToDecimal() const;

        int  getBit(int index) const;
        void setBit(int index, int value);
        void print() const;
    };

}

#endif
