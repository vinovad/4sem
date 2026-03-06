#ifndef BCD_5421_H
#define BCD_5421_H

namespace BCD5421 {
    class BCDNumber {
    private:
        static const int MAX_DIGITS = 32;
        static const int BCD_BASE = 10;
        
        int digits[MAX_DIGITS]; 
        int length;
        
        friend BCDNumber decimalToBCD5421(int decimal);
        friend int bcd5421ToDecimal(BCDNumber bcd);
        friend BCDNumber addBCD5421(BCDNumber a, BCDNumber b);
        
    public:
        BCDNumber() : length(0) {
            for (int i = 0; i < MAX_DIGITS; i++) {
                digits[i] = 0;
            }
        }
        
        int getLength() const {
            return length;
        }
        
        int getDigit(int index) const {
            if (index >= 0 && index < length) {
                return digits[index];
            }
            return 0;
        }
    };
    
    BCDNumber decimalToBCD5421(int decimal);
    int bcd5421ToDecimal(BCDNumber bcd);
    BCDNumber addBCD5421(BCDNumber a, BCDNumber b);
}

#endif