# aclewsample

### dependencies
 - [**pandas**](http://pandas.pydata.org/) (sample.py)
 - [**ffmpeg**](https://www.ffmpeg.org/download.html) (splice.py)
 - [**ffprobe**](https://www.ffmpeg.org/download.html) (templgen.py)
 - [**pympi**](https://github.com/dopefishh/pympi) (templgen.py)

### usage

#### sample.py

sample entries from the ACLEW spreadsheet
```
$ python sample.py aclew_spreadsheet.csv output.csv
```

or as a function:

```python
import sample

df = sample("data/ACLEW_corpora.csv", "output/aclew_sampled.csv")
```


#### splice.py (not done)

splice the selected audio files
```
$ python splice.py input_dir output_dir
```

```input_dir``` is a folder with all the audio files

as a function:

```python
import splice

splice(input_dir="data/audio_input", output_dir="output/spliced_audio_out")
```

#### templgen.py (not done)
choose a random set of 5min regions in a daylong audio file and generate ELAN templates.

```
$ python templgen.py
```
