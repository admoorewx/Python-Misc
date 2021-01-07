from flask import Flask, render_template
import os, time
from folium_mapping import createMap
app = Flask(__name__, template_folder=os.getcwd())

@app.route('/')
def index():
    while True:
        createMap()
        return render_template('map_template.html')
        #time.sleep(300)


if __name__ == "__main__":
    app.run(debug=True)