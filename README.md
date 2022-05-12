Export RoastMaster roast data to Artisan format

### Curve in Roast Master
![Original Roast Curve](screenshots/original.jpg)

### Curve in Artisan

![Artisan Roast Curve](screenshots/artisan.png)


#### How To Use

1. clone this repo
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run it:
```bash
python3 roast_master_plus/artisan.py /path/to/the/parent/directory/of/.dat/files
```
4. import the exported json files (in `artisan/` folder) in Artisan "File -> Import -> Artisan JSON"
