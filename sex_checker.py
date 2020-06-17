#usr/bin/env python3

import argparse
import sys
import os
import pysam
from datetime import datetime
from multiprocessing import Pool
import csv
import pandas as pd
from sklearn.cluster import KMeans

extended_help = """
Input the path to the directory containing the bam files.

To run:
python3 sex_checker_final.py --samplesDir /share/lasallelab/Hyeyeon/projects/DS_DBS/all_samples/ --cores 5 --sampleInfo sample_info_master_updated_DS_DBS.csv
"""

# Input command line arguments
parser = argparse.ArgumentParser(
	description='Check sex of samples.',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	epilog=extended_help)

parser.add_argument(
	'--samplesDir',
	required=False,
	type=str,
	default = None,
	metavar='<path>',
	help='path to a directory of all bam files')

parser.add_argument(
	'--cores',
	required=False,
	type=int,
	default = 1,
	metavar='<int>',
	help='number of cores to use for parallel processing')

parser.add_argument(
	'--sampleInfo',
	required=False,
	type=str,
	default = None,
	metavar='<path>',
	help = "path to csv file that contains sex info for each sample")
	
arg = parser.parse_args()

# Write print statement outputs to file
sys.stdout = open(datetime.now().strftime('%I:%M%p_%b%d') + '_sex_checker.print', 'w')

# Traverses through specified directory and all sub directories
def getBamfiles(path, bamfilePaths):
	for item in os.scandir(path):
		if item.is_file() and item.path.endswith('.bam'):
			bamfilePaths.append(item.path)
		elif item.is_dir():
			bamfilePaths = getBamfiles(item.path, bamfilePaths)
	return (bamfilePaths)	

def countSexChrmReads(bamfile):
	filename = bamfile.split("/")[-1]
	print(filename)
	samplename = filename.split("_")[0]
	print(samplename)		
	
	with open('tempfile.txt', 'a', newline='') as tempfile:
		tempfile = csv.writer(tempfile, delimiter='\t')
		reads = {}
		samfile = pysam.AlignmentFile(bamfile, 'rb')
		reads[bamfile] = {'chrX': 0, 'chrY': 0}
		for read in samfile:
			if read.reference_name in ['chrX', 'chrY'] and read.is_duplicate == False:
				reads[bamfile][read.reference_name] += 1
		
		print(reads[bamfile])
		
		trueSex = getSampleInfo(arg.sampleInfo, samplename)
		
		sexChrmRatio = reads[bamfile]['chrY']/reads[bamfile]['chrX']
		print(sexChrmRatio)	
		tempfile.writerow([
			samplename,
			reads[bamfile]['chrX'],
			reads[bamfile]['chrY'],
			sexChrmRatio,
			sexChrmRatio * 100,
			trueSex
			#sampleInfo.loc[int(samplename), 'Sex']
			])
	
		print(datetime.now())	

def predictSex():
	stats = pd.read_csv("tempfile.txt", sep='\t', engine='python', header=0)
	print(stats)
	# Delete tempfile after reading in
	# os.remove('tempfile.txt')

	# round here because odd rounding behavior occurs when reading in rounded values
	stats['ChrY:ChrX_percent'] = round(stats['ChrY:ChrX_percent'], 5)
	# stats['ChrY:ChrX_percent'] = float('{0:.5f}'.format(stats['ChrY:ChrX_percent']))
		
	kmeansData = stats[['ChrY:ChrX_ratio']].copy()
	# Add placeholder column because kmeans.fit_predict() requires 2D data
	kmeansData['placeholder'] = [0] * len(kmeansData.index)
	kmeans = KMeans(n_clusters = 2)
	predictions = kmeans.fit_predict(kmeansData)
	centers = kmeans.cluster_centers_
	maxCenter = max(centers[0][0], centers[1][0])
	minCenter = min(centers[0][0], centers[1][0])

	if (maxCenter / minCenter) > 2:
	# If the value of one center is greater than 2x the value of the other, both male and female samples exist
		index0 = None
		index1 = None
		if centers[0][0] > centers[1][0]:
			index0 = 'M'
			index1 = 'F'
		else:
			index0 = 'F'
			index1 = 'M'
	
		predictedSex = []
		for predIdx in predictions:
			if predIdx == 0:
				predictedSex.append(index0)
			else:
				predictedSex.append(index1)
	else:
	# Sample are either all male or all female
		predictedSex = ["all M or all F"] * len(predictions)

	stats['Predicted_sex'] = predictedSex

	# Add 'Sex_mismatch' column for any mismatches in the 'Sample_info_sex' and 'Predicted_sex' columns
	# Rows with mismatches are labeled as 'Mismatch'
	# Rows with consistent sex labels are marked with '.'
	sexMismatchList = ['.'] * len(stats.index)
	sampleInfoSex = []
	for i in range(0, len(stats.index)):
		if stats['Sample_info_sex'][i] in ('M' or 'm' or 'Male' or 'male'): 
			sampleInfoSex.append('M')
		if stats['Sample_info_sex'][i] in ('F' or 'f' or 'Female' or 'female'):
			sampleInfoSex.append('F')

	for i in range(0, len(stats.index)):
		if sampleInfoSex[i] != stats['Predicted_sex'][i]:
			print(sampleInfoSex)
			print(stats['Predicted_sex'])
			if stats['Predicted_sex'][i] != "all M or all F":
				sexMismatchList[i] = "Mismatch"
	
	print(sexMismatchList)	
	if len(set(stats['Predicted_sex'])) == 1:
		if len(set(stats['Sample_info_sex'])) != 1:
			sampleInfoMaleCount = sampleInfoSex.count('M')
			sampleInfoFemaleCount = sampleInfoSex.count('F')
			maxCount = max(sampleInfoMaleCount, sampleInfoFemaleCount)
			if maxCount == sampleInfoMaleCount:
			# Mark females as mismatch
				for i in range(0, len(sampleInfoSex)):
					if sampleInfoSex[i] == 'F':
						sexMismatchList[i] = "Mismatch"
			else:
			# Mark males as mismatch
				for i in range(0, len(sampleInfoSex)):
					if sampleInfoSex[i] == 'M':
						sexMismatchList[i] = "Mismatch"

	# Find sex of minority sex in list
	# Set index of that sex to be mismatches
		
	stats['Sex_mismatch'] = sexMismatchList
	stats = stats.sort_values(by = 'Sample_name')
	stats.to_csv(datetime.now().strftime('%I:%M%p_%b%d') + '_sex_checker_output.txt', sep = '\t', index = False)

def getSampleInfo(sampleInfoFile, samplename):
	sampleInfo = pd.read_csv(sampleInfoFile)
	
	if 'Sex' in sampleInfo.columns and 'Name' in sampleInfo.columns:
		sampleInfo.index = list(sampleInfo['Name']) 
		trueSex = sampleInfo.loc[str(samplename), 'Sex']
		return trueSex			
	else:
		print("Sample info csv file must contain the following columns: 'Name', 'Sex'")
		# read first line of csv - should contain header
		# required columns are "Name" and "Sex"
		return 1
	
if __name__ == '__main__':
	timestart = datetime.now()	
	print('timestart = %s' % timestart)

	bamfilePaths = []
	bamfilePaths = getBamfiles(arg.samplesDir, bamfilePaths)
	end_1 = datetime.now()
	print(*bamfilePaths, sep='\n')
	print(len(bamfilePaths))
	print('getBamfiles() %s' % (end_1 - timestart))
	

	samplenames = []
	for bamfile in bamfilePaths:
		filename = bamfile.split("/")[-1]
		print(filename)
		samplename = filename.split("_")[0]
		samplenames.append(samplename)
		with open('tempfile.txt', 'w', newline='') as tempfile:
			tempfile = csv.writer(tempfile, delimiter='\t')
			tempfile.writerow([
				'Sample_name', 'ChrX_reads', 'ChrY_reads', 
				'ChrY:ChrX_ratio', 'ChrY:ChrX_percent',
				'Sample_info_sex'
				])

	
	pool = Pool(processes = arg.cores) 
	pool.map(countSexChrmReads, bamfilePaths)
	pool.close()
	pool.join()
	
	predictSex()
	print('timeend = %s' % (datetime.now() - timestart))
