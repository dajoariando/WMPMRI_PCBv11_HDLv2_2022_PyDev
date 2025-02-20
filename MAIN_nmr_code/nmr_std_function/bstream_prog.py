import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from enum import Enum

class bstream:
	# 220920 the bitstream implementation currently could only take 1 synchronized loop.
	# multiple loop inside a sequence will generate problem due to the implementation of sync.
	# generally, if the individual sequence is created separately, this is not a problem,
	# but the sequence sync functions, i.e. sync_seq, sync_seq_ALL, sync_seq_all_except
	# require sync_in_loop parameter which tells the function whether to ignore the
	# start loop parameter or not. The problem with multiple loops is that we need to give
	# multiple values of sync_in_loop whether we would like to sync in loop for one loop
	# or the other. Workarounds:
	# 1. avoid using sync functions, e.g. sync_seq, sync_seq_ALL, sync_seq_all_except;
	#    which also means programming every single channel individually
	# 2. only use sync functions outside a loop and set the parameter sync_inloop=0
	
	# 220921 the sync function and dump_mem generally has a lot issues. it seems like 
	# the memory being allocated is not correct
	
	
	def __init__(self):
		
		# list of bitstream instances
		self.aux = 0
		self.tx_h1 = 1
		self.tx_l1 = 2
		self.tx_h2 = 3
		self.tx_l2 = 4
		self.tx_charge = 5
		self.tx_charge_bs = 6
		self.tx_dump = 7
		self.tx_clkph = 8
		self.rx_adc_en = 9
		self.rx_in_short = 10
		self.gradZ_p = 11
		self.gradZ_n = 12
		self.BSTREAM_COUNT = 13
		
		# create bitstream objects
		self.bs_objs = [self.bs_obj() for i in range(self.BSTREAM_COUNT)]
		
	def wr_seq (self, pls_pol,seq_end,loop_sta,loop_sto,mux_sel,val, bs_objs_list):
		# write sequence to a list of bitstream objects
		for i in bs_objs_list:
			self.bs_objs[i].wr_seq(pls_pol,seq_end,loop_sta,loop_sto,mux_sel,val)
			
	def wr_seq_ALL (self,pls_pol,seq_end,loop_sta,loop_sto,mux_sel,val):
		bs_objs_list = list(range(0,self.BSTREAM_COUNT,1))
		self.wr_seq(pls_pol,seq_end,loop_sta,loop_sto,mux_sel,val, bs_objs_list)
	
	def calc_seqlen(self, sync_inloop):
		# calculate the sequence length for every bs_obj
		# inloop parameter defines if the sync should be done in a loop or not. This changes the behavior of adding the value
		# of sequence length
		
		seqlenlist = np.zeros(self.BSTREAM_COUNT, dtype=int)
		
		i = 0 # the bs_obj counter number for the loop below
		for a in self.bs_objs:
			seq_end = 0 # sequence end value
			mem_addr = 0 # memory address to be read
			while not seq_end:
				[_, seq_end, loop_sta, loop_sto, _, val] = a.rd_seq(mem_addr); mem_addr += 1 # read the data from the address and increment address
				if loop_sta:
					len_inloop = 0 # accumulate the length of sequence inside loop
					loop_seq_val = val # save the loop sequence value
					loop_sto = 0 # set loop_sto to 0 to initiate next loop
					
					# process the data until finding loop_sto
					while not loop_sto: 
						[_, seq_end, loop_sta, loop_sto, _, val] = a.rd_seq(mem_addr); mem_addr += 1 # read the data from the address and increment address
						len_inloop += val # accumulate the data inside loop
						if seq_end:
							break
					
					if seq_end:	
						# found seq_end inside unterminated loop (no loop_sto), therefore treat it as a sequence like no loop
						# it also implies that it is a loop that is still not done yet and more things inside the loop being
						# written
						seqlenlist[i] += len_inloop
						
					
					if loop_sto:
						# this implies we have found the end of the loop. But depending on if we would like to synchronize in the
						# loop or without the loop, we need to process properly
						if sync_inloop: # sync inside the loop
							seqlenlist[i] += len_inloop
						else:
							# synchronize but without the loop. This implies that there's a sequence that needs to be synchronized
							# but didn't go into the same loop as the reference sequence.
							seqlenlist[i] += (len_inloop*loop_seq_val) # multiply the sequence length inside loop with the loop value

							
				else:
					seqlenlist[i] += val
				
			i += 1 # increment the bs_obj counter number
		
		return seqlenlist
			
	def sync_seq(self, pls_pol, loop_sto, mux_sel, bs_objs_list, sync_inloop):
		# synchronize list of bitstream objects to the longest available sequence
		seqlen = self.calc_seqlen(sync_inloop) # calculate the sequence length and save it into seqlen array
		
		# write sequence to a list of bitstream objects
		for i in bs_objs_list:
			if seqlen[i] < max(seqlen) : # find out if the current seqlen is still smaller than the max 
				self.bs_objs[i].wr_seq(pls_pol,0,0,loop_sto,mux_sel,max(seqlen)-seqlen[i]) # write with the given pulse polarity
	
	def sync_seq_ALL(self, pls_pol, loop_sto, mux_sel, sync_inloop):
		bs_objs_list = list(range(0,self.BSTREAM_COUNT,1))
		self.sync_seq(pls_pol, loop_sto, mux_sel, bs_objs_list, sync_inloop)
		
	def sync_seq_all_except (self, pls_pol, loop_sto, mux_sel, bs_obj_list, sync_inloop):
		# synchronize list of bitstream objects except the one listed in the bs_obj_list
		part_bs_objs_list = list(range(0,self.BSTREAM_COUNT,1)) # create list of all objects
		
		for a in bs_obj_list:
			part_bs_objs_list.remove(a) 
		
		self.sync_seq(pls_pol, loop_sto, mux_sel, part_bs_objs_list, sync_inloop)
	
	def plot_seq (self):
		# calculate the sequence length for every bs_obj
		seqlenlist = np.zeros(self.BSTREAM_COUNT, dtype=int)
		
		i = 0 # the bs_obj counter number for the loop below
		fig, axs = plt.subplots(self.BSTREAM_COUNT, sharex=True, sharey=True)
		for a in self.bs_objs:
			seq_end = 0 # sequence end value
			mem_addr = 0 # memory address to be read
			
			dat = []
			
			while not seq_end:
				[pls_pol, seq_end, loop_sta, loop_sto, mux_sel, val] = a.rd_seq(mem_addr); mem_addr += 1 # read the data from the address and increment address

				
				if loop_sta:
					len_inloop = 0 # accumulate the length of sequence inside loop
					loop_seq_val = val # save the loop sequence value
					loop_sto = 0 # set loop_sto to 0 to initiate next loop
					dat_loop = []
					
					# process the data until finding loop_sto
					while (True):
						[pls_pol, seq_end, loop_sta, loop_sto, mux_sel, val] = a.rd_seq(mem_addr); mem_addr += 1 # read the data from the address and increment address
						
						dat_loop.append([seqlenlist[i]+len_inloop+1,pls_pol])
						dat_loop.append([seqlenlist[i]+len_inloop+val,pls_pol])
						
						len_inloop += val # accumulate the data inside loop
						
						if seq_end:
							dat.append(dat_loop)
							seqlenlist[i] += len_inloop # multiply the sequence length inside loop with the loop value
							break
						
						if loop_sto:
							for i_loop in range(0,loop_seq_val):
								for d in dat_loop:
									d = [d[0]+i_loop*len_inloop,d[1]]
									dat.append(d)
							
							seqlenlist[i] += (len_inloop*loop_seq_val) # multiply the sequence length inside loop with the loop value
							break
								
				else:
					dat.append([seqlenlist[i]+1,pls_pol])
					dat.append([seqlenlist[i]+val,pls_pol])
					
					seqlenlist[i] += val
			
			
			dat_array = np.array(dat)
			dat_array = dat_array.T
			axs[i].plot(dat_array[0],dat_array[1])
			axs[i].ylim = (0,1.1)
			
			i += 1 # increment the bs_obj counter number
		
		# Choose the Slider color
		slider_color = 'White'
		# Set the axis and slider position in the plot
		scroll_slider = plt.axes([0.1, 0.01, 0.8, 0.03],facecolor = slider_color)
		scroll_pos = Slider(scroll_slider,'Pos', 0.1, max(dat_array[0]))
		
		zoom_slider = plt.axes([0.1, 0.03, 0.8, 0.05],facecolor = slider_color)
		zoom_pos = Slider(zoom_slider,'Pos', 1, np.log10(max(dat_array[0])))
		
		def update(val):
		    pos = scroll_pos.val
		    zoom = zoom_pos.val
		    axs[0].axis([pos, pos+(10**zoom), -0.1, 1.1])
		    fig.canvas.draw_idle()
		
		# update function called using on_changed() function
		scroll_pos.on_changed(update)
		zoom_pos.on_changed(update)
		 
		# Display the plot
		plt.show()
		
		pass
	
	def dump_mem (self):
		i = 0; # iteration params
		for a in self.bs_objs:
			seq_end = 0 # sequence end
			mem_addr = 0 # memory address to be read
			print ("##### sequence %d" % (i))
			while not seq_end:
				[pls_pol, seq_end, loop_sta, loop_sto, mux_sel, val] = a.rd_seq(mem_addr); mem_addr += 1 # read the data from the address and increment address
				print("pls_pol=%d  seq_end=%d  loop_sta=%d loop_sto=%d mux_sel=%02d val=%d" %(pls_pol, seq_end, loop_sta, loop_sto, mux_sel, val))
			i += 1	
			
	class bs_obj:
		
		def __init__ (self):
			self.SRAM_DATAWIDTH = 32 # defined by the FPGA
			self.memlen = 128 # the memory length of the bitstream object
			self.meminitval =  1 << ( self.SRAM_DATAWIDTH - 2 ) # the init value of the memory. Set the seq_end bit.
			self.mem = np.full(self.memlen, self.meminitval, dtype=np.int64) # memory of the bitstream (the length is defined by the bitstream object ram size in Quartus)
			self.curr_mem_ofst = 0 # current offset
			self.freq_MHz = 0 # frequency (MHz)
		
		def rst(self): # reset the bitstream to 0
			self.curr_mem_ofst = 0
			self.mem = np.zeros(memlen, dtype=int)
			
		def wr_seq(self, pls_pol,seq_end,loop_sta,loop_sto,mux_sel,val): # write one sequence to the memory
			# pls_pol, seq_end, loop_sta, loop_sto, mux_sel, val
			self.mem[self.curr_mem_ofst] =  ( ( (  pls_pol & 0x01 ) << ( self.SRAM_DATAWIDTH - 1 ) ) | ( (  seq_end & 0x01 ) << ( self.SRAM_DATAWIDTH - 2 ) ) | ( ( loop_sta & 0x01 ) << ( self.SRAM_DATAWIDTH - 3 ) ) | ( (loop_sto & 0x01 ) << ( self.SRAM_DATAWIDTH - 4 ) ) | ( (mux_sel & 0x0F ) << ( self.SRAM_DATAWIDTH - 8 ) ) |  val & 0x0FFFFFFF )
			self.curr_mem_ofst += 1
			
		def rd_seq(self, mem_addr):
			pls_pol = (self.mem[mem_addr] >> ( self.SRAM_DATAWIDTH - 1 )) & 0x01
			seq_end = (self.mem[mem_addr] >> ( self.SRAM_DATAWIDTH - 2 )) & 0x01
			loop_sta = (self.mem[mem_addr] >> ( self.SRAM_DATAWIDTH - 3 )) & 0x01
			loop_sto = (self.mem[mem_addr] >> ( self.SRAM_DATAWIDTH - 4 )) & 0x01
			mux_sel = (self.mem[mem_addr] >> ( self.SRAM_DATAWIDTH - 8 )) & 0x0F
			val = self.mem[mem_addr] & 0x0FFFFFFF
			return [pls_pol, seq_end, loop_sta, loop_sto, mux_sel, val]


def us_to_int_synced (t_us, round_to_int, freq):
	# this function returns t_us in terms of # of clock cycles that is multiplication of round_to_int
	# t_us : time in us
	# round_to_int : round the output to multiplication of this value
	# freq : frequency of clock
	return round_to_int*round((t_us*freq)/round_to_int)
	
def us_to_int (t_us, freq):
	# t_us : time in us
	# freq : frequency of clock
	return round(t_us*freq)


def phenc_bstream (
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
    enc_tao_us,
	):

	SYSCLK_MHz = larmor_clk_fact * f_larmor # calc the bitstream system clock frequency
	
	# precharging params
	lcs_pchg_int = us_to_int_synced(lcs_pchg_us,larmor_clk_fact,SYSCLK_MHz)
	lcs_dump_int = us_to_int_synced(lcs_dump_us,larmor_clk_fact,SYSCLK_MHz)
	
	# echotime	
	echotime_int = us_to_int_synced(echotime_us, 0.5 * larmor_clk_fact, SYSCLK_MHz) # 0.5 * f_larmor is to make sure that the echotime_int is multiplication of (2*SYSCLK_MHz/f_larmor) instead of (SYSCLK_MHz/f_larmor). This is to ensure that if the echotime_int is divided by two, the number is still multiplication of (SYSCLK_MHz/f_larmor). It does not change the absolute length of the echotime.

	# p90 params
	p90_pchg_int = us_to_int_synced(p90_pchg_us, larmor_clk_fact, SYSCLK_MHz)
	p90_pchg_refill_int = us_to_int_synced(p90_pchg_refill_us, larmor_clk_fact, SYSCLK_MHz)
	p90_int = us_to_int_synced(p90_us, larmor_clk_fact, SYSCLK_MHz)
	p90_dchg_int = us_to_int_synced(p90_dchg_us, larmor_clk_fact, SYSCLK_MHz)
	
	# p180 params
	p180_pchg_int = us_to_int_synced(p180_pchg_us, larmor_clk_fact, SYSCLK_MHz)
	p180_pchg_refill_int = us_to_int_synced(p180_pchg_refill_us, larmor_clk_fact, SYSCLK_MHz)
	p180_int = us_to_int_synced(p180_us, larmor_clk_fact, SYSCLK_MHz)
	p180_dchg_int = us_to_int_synced(p180_dchg_us, larmor_clk_fact, SYSCLK_MHz)
	
	# delay params
	d90_int = int (( echotime_int / 2 ) - p90_int - p180_pchg_int - p180_pchg_refill_int)
	d180_int = int(echotime_int - p180_int - p180_pchg_int - p180_pchg_refill_int)

	# additional params
	echoshift_int = us_to_int(echoshift_us, SYSCLK_MHz)
	adc_en_window_int = samples_per_echo * adc_clk_fact
	init_adc_delay_int = int (( echotime_int /2 ) - ( adc_en_window_int /2 ) + echoshift_int)

	# encoding params
	gradlen_int = us_to_int(gradlen_us, SYSCLK_MHz)
	enc_tao_int = us_to_int(enc_tao_us, SYSCLK_MHz)
	
	'''
	TBLANK = 100
	bs.wr_seq(0,0,0,0,0,TBLANK,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2]) # pls_pol, seq_end, loop_sta, loop_sto, mux_sel, val	
	bs.sync_seq(1,0,0,[bs.rx_in_short],0) # set rx_in_short
	bs.sync_seq_ALL(0,0,0,0) # synchronize the others. (pulse_pol, mux_sel)
	seqlenlist = bs.calc_seqlen(0)
	
	bs.wr_seq(1,0,0,0,0,130,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2, bs.aux])
	bs.sync_seq(1,0,0,[bs.rx_in_short,bs.tx_clkph],0) # set rx_in_short and clk phase
	bs.sync_seq_ALL(0,0,0,0) # synchronize the others. (pulse_pol, mux_sel)
	seqlenlist = bs.calc_seqlen(0)
	
	# loop start
	bs.wr_seq_ALL(0,0,1,0,0,echoes_per_scan) # set to all
	
	bs.wr_seq(1,0,0,0,0,120,[bs.tx_dump])
	bs.sync_seq_ALL(0,0,0,1) # synchronize the others. (pulse_pol, mux_sel)
	bs.wr_seq(0,0,0,1,0,120,[bs.tx_dump])
	bs.sync_seq_ALL(0,1,0,1) # synchronize the others. (pulse_pol, mux_sel)
	seqlenlist = bs.calc_seqlen(0)
	
	bs.wr_seq_ALL(0,0,0,0,0,TBLANK) # finish
	bs.wr_seq_ALL(0,1,0,0,0,0) # finish
	'''
	
	# bitstream programmer	
	TBLANK = 10
	bs.wr_seq(0,0,0,0,0,TBLANK,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2]) # pls_pol, seq_end, loop_sta, loop_sto, mux_sel, val	
	bs.sync_seq(1,0,0,[bs.rx_in_short],0) # set rx_in_short
	bs.sync_seq_ALL(0,0,0,0) # synchronize the others. (pulse_pol, mux_sel)
	
	'''
	bs.wr_seq(1,0,0,0,0,lcs_pchg_int,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2, bs.aux])
	bs.sync_seq(1,0,0,[bs.rx_in_short,bs.tx_clkph],0) # set rx_in_short and clk phase
	bs.sync_seq_ALL(0,0,0,0) # synchronize the others. (pulse_pol, mux_sel)
	
	seqlenlist = bs.calc_seqlen(0)
	
	bs.wr_seq(1,0,0,0,0,lcs_dump_int,[bs.tx_dump])
	bs.sync_seq(1,0,0,[bs.rx_in_short,bs.tx_clkph],0) # set rx_in_short and clk phase
	bs.sync_seq_ALL(0,0,0,0) # synchronize the others. (pulse_pol, mux_sel)
	
	seqlenlist = bs.calc_seqlen(0)
	
	bs.wr_seq(1,0,0,0,0,p90_pchg_int+p90_pchg_refill_int,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2, bs.tx_charge])
	bs.sync_seq(1,0,0,[bs.rx_in_short],0) 
	bs.sync_seq(1,0,p90_ph_sel,[bs.tx_clkph],0)
	bs.sync_seq_ALL(0,0,0,0) # synchronize the others. (pulse_pol, mux_sel)
	
	seqlenlist = bs.calc_seqlen(0)
	
	bs.wr_seq(1,0,0,0,0,p90_int,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2, bs.tx_charge_bs])
	bs.sync_seq(1,0,0,[bs.rx_in_short],0) 
	bs.sync_seq(1,0,p90_ph_sel,[bs.tx_clkph],0)
	bs.sync_seq_ALL(0,0,0,0) # synchronize the others. (pulse_pol, mux_sel)
	
	seqlenlist = bs.calc_seqlen(0)
	
	bs.wr_seq(0,0,0,0,0,d90_int,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2])
	if (vvarac<0.0):
		bs.wr_seq(1,0,0,0,0,p90_dchg_int,[bs.tx_dump, bs.gradZ_n])
	else:
		bs.wr_seq(1,0,0,0,0,p90_dchg_int,[bs.tx_dump, bs.gradZ_p])
	bs.sync_seq(1,0,0,[bs.rx_in_short,bs.tx_clkph],0) # set rx_in_short and clk phase
	bs.sync_seq_ALL(0,0,0,0) # synchronize the others. (pulse_pol, mux_sel)
	
	seqlenlist = bs.calc_seqlen(0)
	
	bs.wr_seq(1,0,0,0,0,p180_pchg_int+p180_pchg_refill_int,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2, bs.tx_charge])
	bs.sync_seq(1,0,2,[bs.tx_clkph],0) # set the clockphase to 2
	bs.sync_seq(1,0,0,[bs.rx_in_short],0)
	bs.sync_seq_ALL(0,0,0,0) # synchronize the others. (pulse_pol, mux_sel)
	
	seqlenlist = bs.calc_seqlen(0)
	
	'''
	
	# loop start
	# bs.wr_seq_ALL(0,0,1,0,0,echoes_per_scan) # set to all
	
	bs.wr_seq(1,0,0,0,0,p180_int,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2, bs.tx_charge_bs])
	bs.dump_mem()
	bs.sync_seq(1,0,2,[bs.tx_clkph],0) # set the clockphase to 2
	# bs.sync_seq(1,0,0,[bs.rx_in_short],1)
	# bs.sync_seq_all_except(0,0,0,[bs.rx_adc_en],1)
	
	# bs.wr_seq(0,0,0,0,0,d180_int,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2])
	# bs.wr_seq(1,0,0,0,0,p180_dchg_int,[bs.tx_dump,bs.rx_in_short])
	# bs.sync_seq(1,0,2,[bs.tx_clkph],1) # set the clockphase to 2
	# bs.sync_seq_all_except(0,0,0,[bs.rx_adc_en],1)
	
	# bs.wr_seq(1,0,0,1,0,p180_pchg_int+p180_pchg_refill_int,[bs.tx_h1, bs.tx_h2, bs.tx_l1, bs.tx_l2, bs.rx_in_short])
	# bs.wr_seq(1,0,0,1,0,p180_pchg_int,[bs.tx_charge])
	# bs.sync_seq(1,1,2,[bs.tx_clkph],1) # set the clockphase to 2
	# bs.sync_seq_all_except(0,1,0,[bs.rx_adc_en],1)
	
	# bs.wr_seq(0,0,0,0,0,init_adc_delay_int,[bs.rx_adc_en])
	# bs.wr_seq(1,0,0,0,0,samples_per_echo,[bs.rx_adc_en])
	# bs.sync_seq(1,1,0,[bs.rx_adc_en],1)
	
	# bs.wr_seq_ALL(0,0,0,0,0,TBLANK) # finish
	# bs.wr_seq_ALL(0,1,0,0,0,0) # finish
	
	bs.dump_mem()
	bs.plot_seq()
	
	return lcs_pchg_int