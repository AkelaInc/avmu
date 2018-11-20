
import collections
AvmuComboTuple = collections.namedtuple('AvmuComboTuple', ['tx_idx', 'rx_idx', 'tx_path', 'rx_path'])

def path_the_same(txp, rxp):
	return txp.replace("_TX_", "_RX_") == rxp

def switch_board_type_to_port_list(board_type, is_tx):
	# Switch settings for the TDD and non-TDD boards are the same.
	if board_type == "TDD_4_PORT_SWITCH" or board_type == "SIMPLE_4_PORT_SWITCH":
		if is_tx:
			return ["AVMU_TX_PATH_0", "AVMU_TX_PATH_1", "AVMU_TX_PATH_2", "AVMU_TX_PATH_3"]
		else:
			return ["AVMU_RX_PATH_0", "AVMU_RX_PATH_1", "AVMU_RX_PATH_2", "AVMU_RX_PATH_3"]
	elif board_type == 'NO_SWITCH_BOARD':
		if is_tx:
			return ["AVMU_TX_PATH_0"]
		else:
			return ["AVMU_RX_PATH_1"]
	elif board_type == 'SIMPLE_8_PORT_SWITCH':
		if is_tx:
			return ["AVMU_TX_PATH_0", "AVMU_TX_PATH_1", "AVMU_TX_PATH_2", "AVMU_TX_PATH_3",
					"AVMU_TX_PATH_4", "AVMU_TX_PATH_5", "AVMU_TX_PATH_6", "AVMU_TX_PATH_7"]
		else:
			return ["AVMU_RX_PATH_0", "AVMU_RX_PATH_1", "AVMU_RX_PATH_2", "AVMU_RX_PATH_3",
					"AVMU_RX_PATH_4", "AVMU_RX_PATH_5", "AVMU_RX_PATH_6", "AVMU_RX_PATH_7"]
	elif board_type == 'S_PARAM_SWITCH':
		if is_tx:
			return ["AVMU_TX_PATH_0", "AVMU_TX_PATH_1", "AVMU_TX_PATH_2", "AVMU_TX_PATH_3",
					"AVMU_TX_PATH_4"]
		else:
			return ["AVMU_RX_PATH_0", "AVMU_RX_PATH_1", "AVMU_RX_PATH_2", "AVMU_RX_PATH_3",
					"AVMU_RX_PATH_4"]
	else:
		raise RuntimeError("Invalid switch board type: '%s'" % board_type)

def generate_combo_list(avmu_list, schedule_type):
	combo_listing = []

	# Mask out any disabled avmus so the combos generate properly.
	avmu_list = [tmp for tmp in avmu_list if tmp['AVMU_ENABLE']]

	for tx_avmu in avmu_list:
		tx_avmu_idx = tx_avmu['AVMU_IDX']
		tx_port_list = switch_board_type_to_port_list(tx_avmu['AVMU_SWITCHBOARD_TYPE'], is_tx=True)
		rx_port_list = switch_board_type_to_port_list(tx_avmu['AVMU_SWITCHBOARD_TYPE'], is_tx=False)


		# Since we later require the avmus to have matching
		# switch boards, we can just use the tx avmu for generating both
		for tx_port in tx_port_list:
			for rx_port in rx_port_list:
				tx_set = []

				for rx_avmu in avmu_list:
					rx_avmu_idx = rx_avmu['AVMU_IDX']

					# Sequential scheduling only operates on a per-avmu basis.
					if tx_avmu_idx != rx_avmu_idx and schedule_type == 'SEQUENTIAL':
						continue


					# We need a TDD board to do TDD.
					if tx_avmu['AVMU_DO_TDD'] and tx_avmu['AVMU_SWITCHBOARD_TYPE'] != 'TDD_4_PORT_SWITCH':
						raise RuntimeError("TDD Requires a TDD 4 port switch board! Specified switch board: %s" %
							(tx_avmu['AVMU_SWITCHBOARD_TYPE'], ))

					# Mismatched switch-boards won't do much
					if tx_avmu['AVMU_SWITCHBOARD_TYPE'] != rx_avmu['AVMU_SWITCHBOARD_TYPE']:
						raise RuntimeError("Mismatched switch-board types: %s, %s" %
							(tx_avmu['AVMU_SWITCHBOARD_TYPE'], rx_avmu['AVMU_SWITCHBOARD_TYPE'], ))


					if any([tmp['AVMU_SWITCHBOARD_TYPE'] == 'S_PARAM_SWITCH' for tmp in avmu_list]) and len(avmu_list) > 1:
						raise RuntimeError("S-Param boards can only be run by themselves! Specified switch boards: %s" %
							([tmp['AVMU_SWITCHBOARD_TYPE'] for tmp in avmu_list], ))

					if tx_avmu['AVMU_SWITCHBOARD_TYPE'] == 'S_PARAM_SWITCH':
						tx_num = tx_port.split("_")[-1]
						rx_num = rx_port.split("_")[-1]
						# The valid combos for the s-param board are 0->0, 1->1, 2->2, 3->3, 4->4.

						if tx_num == rx_num:
							avmu_conf = AvmuComboTuple(tx_avmu_idx, rx_avmu_idx, tx_port, rx_port)
							tx_set.append(avmu_conf)

					else:
						# Normal switch boards
						is_transmit = tx_avmu_idx == rx_avmu_idx

						# We can't do monostatic measurements without TDD
						if tx_avmu_idx == rx_avmu_idx and path_the_same(tx_port, rx_port):
							rx_port_masked = "AVMU_RX_PATH_NONE"
						else:
							rx_port_masked = rx_port

						if not is_transmit:
							tx_port_masked = "AVMU_TX_PATH_NONE"
						else:
							tx_port_masked = tx_port

						avmu_conf = AvmuComboTuple(tx_avmu_idx, rx_avmu_idx, tx_port_masked, rx_port_masked)
						if schedule_type == 'SIMULTANEOUS':
							tx_set.append(avmu_conf)
						elif schedule_type == "SEQUENTIAL":
							# Since sequential scheduling is always 1 tx, 1 rx,
							# the combo's where the rx path is RX_PATH_NONE wind
							# up being useless. As such, skip them.
							if rx_port_masked != "AVMU_RX_PATH_NONE":
								tx_set.append(avmu_conf)
						else:
							raise ValueError("Unknown Scheduling mode: %s" % (schedule_type, ))


				if not tx_set:
					# If no paths were generated for the combo,
					# don't append it to the output (this happens
					# mostly in the sequential mode).
					pass
				# If we're doing single-avmu measurements, we don't need to bother
				# with the rx_none paths, since there's no other avmu doing RX.
				elif len(avmu_list) == 1 and tx_set[0].rx_path == 'AVMU_RX_PATH_NONE':
					pass
				else:
					# print("Adding: ", tx_set)
					combo_listing.append(tuple(tx_set))

	for combo in combo_listing:
		fail = any([tmp.rx_path != "AVMU_RX_PATH_NONE" for tmp in combo])
		# if not fail:
		# 	print("Passed conf: ")
		# 	print(avmu_list)
		# 	print(schedule_type)
		# 	print("Computed combos:")
		# 	for it_combo in combo_listing:
		# 		print("	", it_combo)
		assert fail, "At least one avmu must be receiving in every combo: %s" % combo
	return combo_listing

