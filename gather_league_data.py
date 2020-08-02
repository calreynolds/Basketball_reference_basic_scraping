import csv
import time
 

from basic_lebron_stats import *



base_URL = "https://www.basketball-reference.com/"

def main():
	with open('links.csv', newline='') as f:
	    reader = csv.reader(f)
	    data = list(reader)[0]
	players = data[1:]
	steven_adams = data[0]
	print(len(players))
	master_df = return_stats_pipeline(base_URL + steven_adams)
	#master_df1 = return_stats_pipeline(base_URL + data[1])
	none = 0
	for i in range(1, len(players)):
		# Wait for 5 seconds
		#time.sleep(1)
		player_df = return_stats_pipeline(base_URL + players[i])
		if player_df is None:
			print(i)
			none += 1
		else:
			print(i)
			#66/513 - 13 % of data is nulled, leaving 447 total
			master_df = master_df.append(player_df)

	print(str(none) + "/" + str(len(players)))

	master_df.to_csv("out.csv", index=False)


		#print(return_stats_pipeline(base_URL + players[i]))


#630 bad martha's pizza Steve 2 pepp 1 vegg
	#rint(adams_df)

main()