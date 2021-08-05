import flask
from flask import Flask,render_template,request
import pandas as pd                     



app = flask.Flask(__name__)
app.config["DEBUG"] = True


# Function to read 'County' coordinates data from local machine 
def ParseData():
    # Import counties data file form local machine
    path_local = (r'C:\Users\Saif\Downloads\Counties_-_OSi_National_Placenames_Gazetteer.csv')
    df_counties_data = pd.read_csv(path_local)
    
    df_counties = df_counties_data.copy()
    
    # Checking if 'English_Name' and 'County' have same values
    df_counties['English_Name'].equals(df_counties['County'])
    
    # Remove columns name we don't need - Keep columns we need
    df_counties = df_counties[['English_Name','ID', 'IG_E', 'IG_N', 'ITM_E', 'ITM_N']]
    
    # applying convertor function to df_counties | converting tuple to str | remove '(' & ')'
    df_counties['Lat_Long'] = df_counties.apply(lambda x: itm2geo(x['ITM_E'], x['ITM_N']), axis=1).astype(str).apply(lambda x:x.replace('(','')).apply(lambda x:x.replace(')',''))
    
    # convert county names to lower case
    df_counties["English_Name"] = df_counties["English_Name"].str.lower()
    
    # Set 'English_Name' as index
    df_counties.set_index('English_Name',inplace=True)
    df_counties.head(5)
    
    # Convert to dictionary with 'Lat_Long'
    result = df_counties.to_dict()['Lat_Long']
    
    return result
    
    
    

@app.route('/', methods=['GET'])
def home():
    #return "<h1>Welcome to Geocoder :)</h1><p>This is a proof-of-concept API for a Geocoder.</p>"
    return render_template('home_page.html')
    
@app.route('/form')
def form():
    return render_template('form.html')
 
@app.route('/data', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':  
        # Storing user input in form as dicitonary in 'form_data'
        form_data = request.form
        
        # Getting 'County' value from user input
        county_input = form_data['County']
        
        # Calling function to parse 'County' .csv coordinates
        county_dict = ParseData()
        
        # Getting latitude and longitude for county input
        if county_input in county_dict:
            lat_long_coordinates = county_dict[county_input]
            # lat = lat_long_coordinates.split(',')[0]
            # long = lat_long_coordinates.split(',')[1]
            # return "Latitude: " + lat + " - - - - - - - - - - Longitude: " + long
            return render_template('data.html',form_data = lat_long_coordinates)
        else:
            return "Coordinates do not exist. Please check County name!"        
        
        #return county_input
        #return county_dict
        
        #return render_template('data.html',form_data = form_data)


# Function to convert ITM to WGS84 coordinates

from math import *

############################################################################

# Meridian Arc

############################################################################

def arcmer(a,equad,lat1,lat2):

    b=a*sqrt(1-equad)

    n=(a-b)/(a+b)

    a0=1.+((n**2)/4.)+((n**4)/64.)

    a2=(3./2.)*(n-((n**3)/8.))

    a4=(15./16.)*((n**2)-((n**4)/4.))

    a6=(35./48.)*(n**3)



    s1=a/(1+n)*(a0*lat1-a2*sin(2.*lat1)+a4*sin(4.*lat1)-a6*sin(6.*lat1))

    s2=a/(1+n)*(a0*lat2-a2*sin(2.*lat2)+a4*sin(4.*lat2)-a6*sin(6.*lat2))

    return s2-s1

###############################################################################
#
# Transverse Mercator Inverse Projection
#
###############################################################################
def xy2geo(m,p,a,equad,lat0,lon0):

    lat0=radians(lat0)
    lon0=radians(lon0)

    sigma1=p

    fil=lat0+sigma1/(a*(1-equad))

    deltafi=1

    while deltafi > 0.0000000001:

        sigma2=arcmer(a,equad,lat0,fil)

        RO=a*(1-equad)/((1-equad*(sin(fil)**2))**(3./2.))

        deltafi=(sigma1-sigma2)/RO

        fil=fil+deltafi 


    N=a/sqrt(1-equad*(sin(fil))**2)

    RO=a*(1-equad)/((1-equad*(sin(fil)**2))**(3./2.))

    t=tan(fil)

    psi=N/RO

    lat=fil-(t/RO)*((m**2)/(2.*N))+(t/RO)*((m**4)/(24.*(N**3)))*(-4.*(psi**2)-9.*psi*(1.-t**2)+12.*(t**2))-(t/RO)*(m**6/(720.*(N**5)))*(8.*(psi**4)*(11.-24.*(t**2))-12.*(psi**3)*(21.-71.*(t**2))+15.*(psi**2)*(15.-98.*(t**2)+15.*(t**4))+180.*psi*(5.*(t**2)-3.*(t**4))-360.*(t**4))+(t/RO)*((m**8)/(40320.*(N**7)))*(1385.+3633.*(t**2)+4095.*(t**4)+1575.*(t**6))

    lon=(m/(N))-((m**3)/(6.*(N**3)))*(psi+2.*(t**2))+((m**5)/(120.*(N**5)))*(-4.*(psi**3)*(1.-6.*(t**2))+(psi**2)*(9.-68.*(t**2))+72.*psi*(t**2)+24.*(t**4))-((m**7)/(5040.*(N**7)))*(61.+662.*(t**2)+1320.*(t**4)+720.*(t**6))

    lon=lon0+lon/cos(fil)

    lat=degrees(lat)
    lon=degrees(lon)

    return lat,lon


#############################################################################

# Irish Transverse Mercator - Inverse

#############################################################################

def itm2geo(x,y):

    # GRS-80

    a = 6378137.

    equad =0.00669437999        

    # Natural Origin 

    lat0=53.5

    lon0=-8.

    k0=0.999820

    p = (y - 750000.) /k0

    m = (x - 600000.) /k0

    lat,lon = xy2geo(m,p,a,equad,lat0,lon0)

    return lat,lon    



if __name__ == '__main__':
   app.run(host='192.168.1.13')  # *change host IP address (ipv4) depending on network connection
   #app.run(host='0.0.0.0', debug=True)
   
