# Sylvio Dos Reis, Micah Yoon, 2026
# Downloads and uncompresses the mandatory high and low resolution worldwide elevation datas.

mkdir $DIR/geog
cd $DIR/geog
wget https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_high_res_mandatory.tar.gz
tar -xzf geog_high_res_mandatory.tar.gz --strip-components=1
rm -rf geog_high_res_mandatory.tar.gz
wget https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_low_res_mandatory.tar.gz
tar -xzf geog_low_res_mandatory.tar.gz --strip-components=1
rm -rf geog_low_res_mandatory.tar.gz