# SexChecker
#### Check sex of samples using BAM files, k-means clustering, and the number of reads in the sex chromosomes of samples. <br>

## Input command line arguments
1. `--samplesDir` <path> Path to a directory containing BAM files of all samples or subdirectories of the BAM files. <br>
2. `--cores` <int> Number of cores to use for multiprocessing. Default is 1. <br>
3. `--sampleInfo` <path> Path to a sample info .csv file. Must contain `Name` and `Sex` columns for each sample.
  
## Algorithm
1. Calculate sex chromosome ratios for each sample. <br><br>
![ratio](https://latex.codecogs.com/gif.latex?Sex%5C%3Achromosome%5C%3Aratio%20%3D%20%5Cfrac%7BNumber%5C%3Aof%5C%3AChrY%5C%3Areads%7D%7BNumber%5C%3Aof%5C%3AChrX%5C%3Areads%7D) <br><br>
2. For k-means clustering, `k = 2` to represent the male and female sexes. All sex chromosome read ratios are divided into two clusters. 
* If the value of one cluster center is greater than two the value of the second cluster center, then both male and female samples exist. The sex of samples will be predicted as `M` or `F`. 
* Otherwise, the sex prediction will be recorded as `all M or all F`. <br>
  
## Output
If there is a mismatch between the predicted sex of a sample and its recorded sex in the sample info file, the `Mismatch` column in the output file will record `Mismatch`. Otherwise, if the predicted sex is the same as the sample info sex, a single period `.` will be recorded in the `Mismatch` column.
1. `sex_checker_[current date and time].print` Stores all print statements.
2. `sex_checker_output_[current date and time].txt` Output of sex checker in tab-delimited format. 

## Example of output file
| Sample_name | ChrX_reads | ChrY_reads | ChrY:ChrX_ratio | ChrY:ChrX_percent | Predicted_sex | Sample_info_sex | Mismatch
| --------------- | --------------- | --------------- | --------------- | --------------- | --------------- | --------------- | --------------- |
| Sample_1 | 4890507 |20417 | 0.004174823 | 0.41748 | F |	F | . |
| Sample_2 | 5550573| 24946	| 0.004494311	| 0.44943 | F | M | Mismatch |
| Sample_3 | 2990996| 356739 | 0.119270972 | 11.9271 | M | M | . |

