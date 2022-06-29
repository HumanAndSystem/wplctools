enum Device {
    DevSkip = -2,
    DevError = -1,
    DevNone = 0,
    DevDot = 1,
    DevAt = 2,
    DevA = 3,
    DevB = 4,
    DevC = 5,
    DevD = 6,
    DevE = 7,
    DevF = 8,
    DevG = 9,
    DevH = 10,
    DevI = 11,
    DevJ = 12,
    DevK = 13,
    DevL = 14,
    DevM = 15,
    DevN = 16,
    DevO = 17,
    DevP = 18,
    DevQ = 19,
    DevR = 20,
    DevS = 21,
    DevT = 22,
    DevU = 23,
    DevV = 24,
    DevW = 25,
    DevX = 26,
    DevY = 27,
    DevZ = 28,
    DevSep = 29,
    DevBL = 30,
    DevCC = 31,
    DevCN = 32,
    DevCS = 33,
    DevDX = 34,
    DevDY = 35,
    DevED = 36,
    DevFD = 37,
    DevFX = 38,
    DevFY = 39,
    DevHD = 40,
    DevKD = 41,
    DevLB = 42,
    DevLC = 43,
    DevLT = 44,
    DevLW = 45,
    DevLX = 46,
    DevLY = 47,
    DevLZ = 48,
    DevRD = 49,
    DevSB = 50,
    DevSD = 51,
    DevSM = 52,
    DevST = 53,
    DevSW = 54,
    DevTC = 55,
    DevTN = 56,
    DevTS = 57,
    DevZR = 58,
    DevZZ = 59,
    DevLCC = 60,
    DevLCN = 61,
    DevLCS = 62,
    DevLST = 63,
    DevLTC = 64,
    DevLTN = 65,
    DevLTS = 66,
    DevSTC = 67,
    DevSTN = 68,
    DevSTS = 69,
    DevLSTC = 70,
    DevLSTN = 71,
    DevLSTS = 72,
};

char* code_to_name(int code) {
    switch (code) {
        case DevDot: return ".";
        case DevAt: return "@";
        case DevA: return "A";
        case DevB: return "B";
        case DevC: return "C";
        case DevD: return "D";
        case DevE: return "E";
        case DevF: return "F";
        case DevG: return "G";
        case DevH: return "H";
        case DevI: return "I";
        case DevJ: return "J";
        case DevK: return "K";
        case DevL: return "L";
        case DevM: return "M";
        case DevN: return "N";
        case DevO: return "O";
        case DevP: return "P";
        case DevQ: return "Q";
        case DevR: return "R";
        case DevS: return "S";
        case DevT: return "T";
        case DevU: return "U";
        case DevV: return "V";
        case DevW: return "W";
        case DevX: return "X";
        case DevY: return "Y";
        case DevZ: return "Z";
        case DevSep: return "\\";
        case DevBL: return "BL";
        case DevCC: return "CC";
        case DevCN: return "CN";
        case DevCS: return "CS";
        case DevDX: return "DX";
        case DevDY: return "DY";
        case DevED: return "ED";
        case DevFD: return "FD";
        case DevFX: return "FX";
        case DevFY: return "FY";
        case DevHD: return "HD";
        case DevKD: return "KD";
        case DevLB: return "LB";
        case DevLC: return "LC";
        case DevLT: return "LT";
        case DevLW: return "LW";
        case DevLX: return "LX";
        case DevLY: return "LY";
        case DevLZ: return "LZ";
        case DevRD: return "RD";
        case DevSB: return "SB";
        case DevSD: return "SD";
        case DevSM: return "SM";
        case DevST: return "ST";
        case DevSW: return "SW";
        case DevTC: return "TC";
        case DevTN: return "TN";
        case DevTS: return "TS";
        case DevZR: return "ZR";
        case DevZZ: return "ZZ";
        case DevLCC: return "LCC";
        case DevLCN: return "LCN";
        case DevLCS: return "LCS";
        case DevLST: return "LST";
        case DevLTC: return "LTC";
        case DevLTN: return "LTN";
        case DevLTS: return "LTS";
        case DevSTC: return "STC";
        case DevSTN: return "STN";
        case DevSTS: return "STS";
        case DevLSTC: return "LSTC";
        case DevLSTN: return "LSTN";
        case DevLSTS: return "LSTS";
    };
    return "?";
};

class lexer {
private:
    char* _p;
    char* _end;
    int end() {
        return this->_p >= this->_end;
    }
    int p(int i = 0) {
        return this->_p[i];
    }
    void seek(int n = 1) {
        this->_p += n;
    }
    int scan_name() {
        switch (this->p(0)) {
            case '.': this->seek(1); return DevDot;
            case '@': this->seek(1); return DevAt;
            case 'a':
            case 'A': this->seek(1); return DevA;
            case 'b':
            case 'B': switch (this->p(1)) {
                    case 'l':
                    case 'L': this->seek(2); return DevBL;
                    default: this->seek(1); return DevB;
                }
                return DevError;
            case 'c':
            case 'C': switch (this->p(1)) {
                    case 'c':
                    case 'C': this->seek(2); return DevCC;
                    case 'n':
                    case 'N': this->seek(2); return DevCN;
                    case 's':
                    case 'S': this->seek(2); return DevCS;
                    default: this->seek(1); return DevC;
                }
                return DevError;
            case 'd':
            case 'D': switch (this->p(1)) {
                    case 'x':
                    case 'X': this->seek(2); return DevDX;
                    case 'y':
                    case 'Y': this->seek(2); return DevDY;
                    default: this->seek(1); return DevD;
                }
                return DevError;
            case 'e':
            case 'E': switch (this->p(1)) {
                    case 'd':
                    case 'D': this->seek(2); return DevED;
                    default: this->seek(1); return DevE;
                }
                return DevError;
            case 'f':
            case 'F': switch (this->p(1)) {
                    case 'd':
                    case 'D': this->seek(2); return DevFD;
                    case 'x':
                    case 'X': this->seek(2); return DevFX;
                    case 'y':
                    case 'Y': this->seek(2); return DevFY;
                    default: this->seek(1); return DevF;
                }
                return DevError;
            case 'g':
            case 'G': this->seek(1); return DevG;
            case 'h':
            case 'H': switch (this->p(1)) {
                    case 'd':
                    case 'D': this->seek(2); return DevHD;
                    default: this->seek(1); return DevH;
                }
                return DevError;
            case 'i':
            case 'I': this->seek(1); return DevI;
            case 'j':
            case 'J': this->seek(1); return DevJ;
            case 'k':
            case 'K': switch (this->p(1)) {
                    case 'd':
                    case 'D': this->seek(2); return DevKD;
                    default: this->seek(1); return DevK;
                }
                return DevError;
            case 'l':
            case 'L': switch (this->p(1)) {
                    case 'b':
                    case 'B': this->seek(2); return DevLB;
                    case 'c':
                    case 'C': switch (this->p(2)) {
                            case 'c':
                            case 'C': this->seek(3); return DevLCC;
                            case 'n':
                            case 'N': this->seek(3); return DevLCN;
                            case 's':
                            case 'S': this->seek(3); return DevLCS;
                            default: this->seek(2); return DevLC;
                        }
                        return DevError;
                    case 's':
                    case 'S': switch (this->p(2)) {
                            case 't':
                            case 'T': switch (this->p(3)) {
                                    case 'n':
                                    case 'N': this->seek(4); return DevLSTN;
                                    case 's':
                                    case 'S': this->seek(4); return DevLSTS;
                                    default: this->seek(3); return DevLST;
                                }
                                return DevError;
                            default: return DevError;
                        }
                        return DevError;
                    case 't':
                    case 'T': switch (this->p(2)) {
                            case 'c':
                            case 'C': this->seek(3); return DevLTC;
                            case 'n':
                            case 'N': this->seek(3); return DevLTN;
                            case 's':
                            case 'S': this->seek(3); return DevLTS;
                            default: this->seek(2); return DevLT;
                        }
                        return DevError;
                    case 'w':
                    case 'W': this->seek(2); return DevLW;
                    case 'x':
                    case 'X': this->seek(2); return DevLX;
                    case 'y':
                    case 'Y': this->seek(2); return DevLY;
                    case 'z':
                    case 'Z': this->seek(2); return DevLZ;
                    default: this->seek(1); return DevL;
                }
                return DevError;
            case 'm':
            case 'M': this->seek(1); return DevM;
            case 'n':
            case 'N': this->seek(1); return DevN;
            case 'o':
            case 'O': this->seek(1); return DevO;
            case 'p':
            case 'P': this->seek(1); return DevP;
            case 'q':
            case 'Q': this->seek(1); return DevQ;
            case 'r':
            case 'R': switch (this->p(1)) {
                    case 'd':
                    case 'D': this->seek(2); return DevRD;
                    default: this->seek(1); return DevR;
                }
                return DevError;
            case 's':
            case 'S': switch (this->p(1)) {
                    case 'b':
                    case 'B': this->seek(2); return DevSB;
                    case 'd':
                    case 'D': this->seek(2); return DevSD;
                    case 'm':
                    case 'M': this->seek(2); return DevSM;
                    case 't':
                    case 'T': switch (this->p(2)) {
                            case 'c':
                            case 'C': this->seek(3); return DevSTC;
                            case 'n':
                            case 'N': this->seek(3); return DevSTN;
                            case 's':
                            case 'S': this->seek(3); return DevSTS;
                            default: this->seek(2); return DevST;
                        }
                        return DevError;
                    case 'w':
                    case 'W': this->seek(2); return DevSW;
                    default: this->seek(1); return DevS;
                }
                return DevError;
            case 't':
            case 'T': switch (this->p(1)) {
                    case 'c':
                    case 'C': this->seek(2); return DevTC;
                    case 'n':
                    case 'N': this->seek(2); return DevTN;
                    case 's':
                    case 'S': this->seek(2); return DevTS;
                    default: this->seek(1); return DevT;
                }
                return DevError;
            case 'u':
            case 'U': this->seek(1); return DevU;
            case 'v':
            case 'V': this->seek(1); return DevV;
            case 'w':
            case 'W': this->seek(1); return DevW;
            case 'x':
            case 'X': this->seek(1); return DevX;
            case 'y':
            case 'Y': this->seek(1); return DevY;
            case 'z':
            case 'Z': switch (this->p(1)) {
                    case 'r':
                    case 'R': this->seek(2); return DevZR;
                    case 'z':
                    case 'Z': this->seek(2); return DevZZ;
                    default: this->seek(1); return DevZ;
                }
                return DevError;
            case '/':
            case '\\': this->seek(1); return DevSep;
            case '0':
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9': return DevNone;
            case '%': this->seek(1); return DevSkip;
            default: return DevError;
        }
        return DevError;
    }
    int scan_dec() {
        int n = -1;
        while (!this->end()) {
            int c = this->p(0);
            switch (c) {
                case '0': c = 0; break;
                case '1': c = 1; break;
                case '2': c = 2; break;
                case '3': c = 3; break;
                case '4': c = 4; break;
                case '5': c = 5; break;
                case '6': c = 6; break;
                case '7': c = 7; break;
                case '8': c = 8; break;
                case '9': c = 9; break;
                default: return n;
            }
            n = (n < 0) ? c : (n * 10 + c);
            this->seek(1);
        }
        return n;
    }
    int scan_hex() {
        int n = -1;
        while (!this->end()) {
            int c = this->p(0);
            switch (c) {
                case '0': c = 0; break;
                case '1': c = 1; break;
                case '2': c = 2; break;
                case '3': c = 3; break;
                case '4': c = 4; break;
                case '5': c = 5; break;
                case '6': c = 6; break;
                case '7': c = 7; break;
                case '8': c = 8; break;
                case '9': c = 9; break;
                case 'A': c = 10; break;
                case 'B': c = 11; break;
                case 'C': c = 12; break;
                case 'D': c = 13; break;
                case 'E': c = 14; break;
                case 'F': c = 15; break;
                case 'a': c = 10; break;
                case 'b': c = 11; break;
                case 'c': c = 12; break;
                case 'd': c = 13; break;
                case 'e': c = 14; break;
                case 'f': c = 15; break;
                default: return n;
            }
            n = (n < 0) ? c : (n * 16 + c);
            this->seek(1);
        }
        return n;
    }
    int scan_device(DEVs& devs) {
        while (!this->end()) {
            int code = this->scan_name();
            int num = -1;
            switch (code) {
                case DevError:
                    return 0;
                case DevSkip:
                    continue;
                case DevAt:
                case DevSep:
                    num = 0;
                    break;
                case DevX:
                case DevY:
                case DevB:
                case DevW:
                case DevDot:
                case DevDX:
                case DevDY:
                case DevFX:
                case DevFY:
                    num = this->scan_hex();
                    break;
                default:
                    num = this->scan_dec();
                    break;
            }
            devs.add(code, num);
        }
    }
public:
    int scan(char* p, int length, DEVs& devs) {
        this->_p = p;
        if (length < 0) {
            length = (int)strlen(p);
        }
        this->_end = p + length;
        return this->scan_device(devs);
    }
};
