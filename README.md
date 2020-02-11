# XplaneToStellarium

connects X-plane 10/11 to Stellarium for celestial navigation methods. 

For a ful tutorial on Celestial Navigation see this[MUDSPIKE.COM LINK] article on Mudspike.com. 

# Requirements: 

Python 3 - https://www.python.org/downloads/
Stellarium 0.18.2 - https://stellarium.org/

Note: This may work with different versions

Install python 3, this will require no further configuration. 

Once Stellarium is installed open it and go to Configuration > Plugins screen and enable the Remote Control plugin(V 0.0.3). 

Configure the Remote Control Plugin by selecting 'Server Enabled' and 'Load on Start up' checkmarks.

Once this has been configured all you need to do is start up stellarium and X-plane before opening this Python script. 

# Usage 

Run this script on the same computer as which you are running Stellarium. Start up a command line window in the directory where main.py has been extracted or simple double click on the run.bat file. 

The application will ask for a IP and PORT to use, if you are running X-plane on the same computer you will have to do nothing and simply press enter to continue. If you have X-plane running on a different computer please put in the IP of that machine. The port is the standard X-plane communications port(49000).

In X-plane you can check Net Connections > Data to see what X-plane currently is communicating. 

Once both IP and Port have been put in the application will start communicating with X-plane and will set the position in Stellarium. You will see the sky change from the default sky in Stellarium and on the bottom left it will read 'Earth, X-plane' as location.

See this[DISCUSSION THREAD] thread on Mudspike.com if you have any questions or for further information! 

Happy flying! 
