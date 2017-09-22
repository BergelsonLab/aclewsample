# aclewsample

### dependencies
 - pandas
 - ffmpeg
 - ffprobe

### usage

#### sample.py

sample from the ACLEW spreadsheet
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
$ python splice.py aclew_sampled.csv input_dir output_dir
```

```input_dir``` is a folder with all the audio files

as a function:

```python
import sample
import splice

sampled_df = sample("data/ACLEW_corpora.csv", "output/aclew_sampled.csv")

splice(sampled_df, "data/audio_input", "output/spliced_output")
```

#### templgen.py (not done)
generate Pratt templates for the spliced files

TODO...
