#include <sst/core/sst_config.h>
#include <sst/core/rng/marsaglia.h>
#include "HyperPonger.h"
#include "GlobalParams.h"

class BallEvent : public SST::Event {
  public:
    BallEvent() : SST::Event(), count(0) { }
    BallEvent(int64_t cnt) : SST::Event(), count(cnt) { }
    
    int64_t count;

    void serialize_order(SST::Core::Serialization::serializer &ser)  override {
      Event::serialize_order(ser);
      ser & count;
    }

    // Register this event as serializable
    ImplementSerializable(BallEvent);
};

static double artificialWorkValue = 1.1;
static double artificialWorkMultiplier = 1.23;
static void conductArtificialWork(int64_t count) {
  for(int64_t i = 0; i < count; i++) {
    artificialWorkValue *= artificialWorkMultiplier;
  }
}

HyperPonger::HyperPonger( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  rng = new SST::RNG::MarsagliaRNG();
  initialBalls = params.find<int64_t>("numBalls", 0);

  linkN = configureLink("port_n", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  linkS = configureLink("port_s", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  linkW = configureLink("port_w", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  linkE = configureLink("port_e", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  
  hyperLink[0] = configureLink("port_0", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[1] = configureLink("port_1", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[2] = configureLink("port_2", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[3] = configureLink("port_3", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[4] = configureLink("port_4", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[5] = configureLink("port_5", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[6] = configureLink("port_6", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[7] = configureLink("port_7", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[8] = configureLink("port_8", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[9] = configureLink("port_9", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[10] = configureLink("port_10", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[11] = configureLink("port_11", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[12] = configureLink("port_12", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[13] = configureLink("port_13", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[14] = configureLink("port_14", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[15] = configureLink("port_15", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[16] = configureLink("port_16", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[17] = configureLink("port_17", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[18] = configureLink("port_18", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[19] = configureLink("port_19", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[20] = configureLink("port_20", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[21] = configureLink("port_21", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[22] = configureLink("port_22", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[23] = configureLink("port_23", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[24] = configureLink("port_24", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[25] = configureLink("port_25", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[26] = configureLink("port_26", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[27] = configureLink("port_27", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[28] = configureLink("port_28", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[29] = configureLink("port_29", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[30] = configureLink("port_30", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[31] = configureLink("port_31", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[32] = configureLink("port_32", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[33] = configureLink("port_33", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[34] = configureLink("port_34", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[35] = configureLink("port_35", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[36] = configureLink("port_36", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[37] = configureLink("port_37", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[38] = configureLink("port_38", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[39] = configureLink("port_39", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[40] = configureLink("port_40", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[41] = configureLink("port_41", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[42] = configureLink("port_42", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[43] = configureLink("port_43", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[44] = configureLink("port_44", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[45] = configureLink("port_45", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[46] = configureLink("port_46", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[47] = configureLink("port_47", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[48] = configureLink("port_48", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[49] = configureLink("port_49", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[50] = configureLink("port_50", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[51] = configureLink("port_51", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[52] = configureLink("port_52", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[53] = configureLink("port_53", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[54] = configureLink("port_14", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[55] = configureLink("port_15", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[56] = configureLink("port_56", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[57] = configureLink("port_57", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[58] = configureLink("port_58", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[59] = configureLink("port_59", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[60] = configureLink("port_60", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[61] = configureLink("port_61", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[62] = configureLink("port_62", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[63] = configureLink("port_63", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[64] = configureLink("port_64", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[65] = configureLink("port_65", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[66] = configureLink("port_66", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[67] = configureLink("port_67", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[68] = configureLink("port_68", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[69] = configureLink("port_69", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[70] = configureLink("port_70", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[71] = configureLink("port_71", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[72] = configureLink("port_72", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[73] = configureLink("port_73", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[74] = configureLink("port_74", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[75] = configureLink("port_75", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[76] = configureLink("port_76", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[77] = configureLink("port_77", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[78] = configureLink("port_78", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[79] = configureLink("port_79", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[80] = configureLink("port_80", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[81] = configureLink("port_81", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[82] = configureLink("port_82", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[83] = configureLink("port_83", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[84] = configureLink("port_84", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[85] = configureLink("port_85", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[86] = configureLink("port_86", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[87] = configureLink("port_87", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[88] = configureLink("port_88", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[89] = configureLink("port_89", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[90] = configureLink("port_90", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[91] = configureLink("port_91", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[92] = configureLink("port_92", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[93] = configureLink("port_93", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[94] = configureLink("port_94", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[95] = configureLink("port_95", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[96] = configureLink("port_96", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[97] = configureLink("port_97", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[98] = configureLink("port_98", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[99] = configureLink("port_99", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[100] = configureLink("port_100", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[101] = configureLink("port_101", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[102] = configureLink("port_102", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[103] = configureLink("port_103", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[104] = configureLink("port_104", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[105] = configureLink("port_105", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[106] = configureLink("port_106", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[107] = configureLink("port_107", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[108] = configureLink("port_108", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[109] = configureLink("port_109", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[110] = configureLink("port_110", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[111] = configureLink("port_111", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[112] = configureLink("port_112", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[113] = configureLink("port_113", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[114] = configureLink("port_114", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[115] = configureLink("port_115", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[116] = configureLink("port_116", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[117] = configureLink("port_117", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[118] = configureLink("port_118", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[119] = configureLink("port_119", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[120] = configureLink("port_120", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[121] = configureLink("port_121", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[122] = configureLink("port_122", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[123] = configureLink("port_123", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[124] = configureLink("port_124", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[125] = configureLink("port_125", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[126] = configureLink("port_126", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[127] = configureLink("port_127", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[128] = configureLink("port_128", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[129] = configureLink("port_129", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[130] = configureLink("port_130", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[131] = configureLink("port_131", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[132] = configureLink("port_132", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[133] = configureLink("port_133", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[134] = configureLink("port_134", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[135] = configureLink("port_135", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[136] = configureLink("port_136", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[137] = configureLink("port_137", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[138] = configureLink("port_138", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[139] = configureLink("port_139", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[140] = configureLink("port_140", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[141] = configureLink("port_141", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[142] = configureLink("port_142", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[143] = configureLink("port_143", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[144] = configureLink("port_144", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[145] = configureLink("port_145", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[146] = configureLink("port_146", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[147] = configureLink("port_147", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[148] = configureLink("port_148", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[149] = configureLink("port_149", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[150] = configureLink("port_150", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[151] = configureLink("port_151", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[152] = configureLink("port_152", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[153] = configureLink("port_153", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[154] = configureLink("port_154", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[155] = configureLink("port_155", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[156] = configureLink("port_156", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[157] = configureLink("port_157", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[158] = configureLink("port_158", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[159] = configureLink("port_159", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[160] = configureLink("port_160", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[161] = configureLink("port_161", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[162] = configureLink("port_162", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[163] = configureLink("port_163", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[164] = configureLink("port_164", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[165] = configureLink("port_165", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[166] = configureLink("port_166", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[167] = configureLink("port_167", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[168] = configureLink("port_168", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[169] = configureLink("port_169", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[170] = configureLink("port_170", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[171] = configureLink("port_171", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[172] = configureLink("port_172", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[173] = configureLink("port_173", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[174] = configureLink("port_174", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[175] = configureLink("port_175", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[176] = configureLink("port_176", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[177] = configureLink("port_177", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[178] = configureLink("port_178", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[179] = configureLink("port_179", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[180] = configureLink("port_180", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[181] = configureLink("port_181", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[182] = configureLink("port_182", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[183] = configureLink("port_183", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[184] = configureLink("port_184", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[185] = configureLink("port_185", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[186] = configureLink("port_186", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[187] = configureLink("port_187", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[188] = configureLink("port_188", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[189] = configureLink("port_189", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));

  hyperLink[190] = configureLink("port_190", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[191] = configureLink("port_191", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[192] = configureLink("port_192", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[193] = configureLink("port_193", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[194] = configureLink("port_194", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[195] = configureLink("port_195", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[196] = configureLink("port_196", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[197] = configureLink("port_197", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[198] = configureLink("port_198", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
  hyperLink[199] = configureLink("port_199", new SST::Event::Handler<HyperPonger>(this, &HyperPonger::handleEvent));
}

HyperPonger::~HyperPonger() { }

void HyperPonger::setup() {
  for(int i = 0; i < initialBalls; i++) {
    sendOutRandomBall();
  }
}

void HyperPonger::finish() { }

bool HyperPonger::tick( SST::Cycle_t currentCycle ) {
  return false;
}

void HyperPonger::handleEvent(SST::Event *ev) {
  conductArtificialWork(gArtificialWork);
  sendOutRandomBall();
  delete ev;
}

void HyperPonger::sendOutRandomBall() {
  int rndNumber;
  rndNumber = (int)(rng->generateNextInt32());
  rndNumber = (rndNumber & 0x0000FFFF) ^ ((rndNumber & 0xFFFF0000) >> 16);
  rndNumber = abs((int)(rndNumber % 204));

       if(rndNumber == 0) { linkN->send(new BallEvent(1)); }
  else if(rndNumber == 1) { linkS->send(new BallEvent(1)); }
  else if(rndNumber == 2) { linkW->send(new BallEvent(1)); }
  else if(rndNumber == 3) { linkE->send(new BallEvent(1)); }
  else {
    int hyperPort = rndNumber - 4;
    hyperLink[hyperPort]->send(new BallEvent(1));
  }
}
