# SexChecker
Check sex of samples using BAM files and k-means clustering and the number of reads in the sex chromosomes. If there is a mismatch between the predicted sex of a sample and its recorded sex in the sample info file, the "Mismatch" column in the output file will record `Mismatch`. Otherwise, if the predicted sex is the same as the sample info sex, a single period `.` will be recorded in the "Mismatch" column.

## Input command line arguments
`--samplesDir` <path> Path to a directory of BAM files for all samples. <br>
`--cores` <int> Number of cores to use for multiprocessing. Default is 1. <br>
`--sampleInfo` <path> Path to a sample info csv file that contains the sex data for each sample.
  
## Output
`sex_checker.print` Stores all print statements
`sex_checker_output.txt` Output of sex checker in tab-delimited format.

### Example of output file
| Sample_name | ChrX_reads | ChrY_reads | ChrY:ChrX_ratio | ChrY:ChrX_percent | Predicted_sex | Sample_info_sex | Mismatch
| --------------- | --------------- | --------------- | --------------- | --------------- | --------------- | --------------- | --------------- |
| Sample_1 | 4890507 |20417 | 0.004174823 | 0.41748 | F |	F | . |
| Sample_2 | 5550573| 24946	| 0.004494311	| 0.44943 | F | M | Mismatch |
| Sample_3 | 2990996| 356739 | 0.119270972 | 11.9271 | M | M | . |

