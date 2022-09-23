from bstream_prog import phenc_bstream
from bstream_prog import bstream

bs = bstream()

f_larmor=4.00
larmor_clk_fact=16
adc_clk_fact=4
bstrap_pchg_us=10
lcs_pchg_us=3
lcs_dump_us=4
p90_pchg_us=5
p90_pchg_refill_us=2
p90_us=5
p90_dchg_us=3
p90_dtcl=0.5
p180_pchg_us=0.5
p180_pchg_refill_us=p90_pchg_refill_us*1.6
p180_us=p90_us*1.6
p180_dchg_us=p90_dchg_us
p180_dtcl=0.5
echoshift_us=1
echotime_us=20
samples_per_echo=4
echoes_per_scan=2
p90_ph_sel=1
dconv_fact=1
echoskip=1
echodrop=1
gradlen_us=5
enc_tao_us=10
vvarac = -3.0

x = phenc_bstream (
    bs,
    f_larmor,
    larmor_clk_fact,
    adc_clk_fact,
    bstrap_pchg_us,
    lcs_pchg_us,
    lcs_dump_us,
    p90_pchg_us,
    p90_pchg_refill_us,
    p90_us,
    p90_dchg_us,
    p90_dtcl,
    p180_pchg_us,
    p180_pchg_refill_us,
    p180_us,
    p180_dchg_us,
    p180_dtcl,
    echoshift_us,
    echotime_us,
    samples_per_echo,
    echoes_per_scan,
    p90_ph_sel,
    dconv_fact,
    echoskip,
    echodrop,
    vvarac,
    gradlen_us,
    enc_tao_us
    );