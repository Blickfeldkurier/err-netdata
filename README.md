# Err-Netdata
[Errbot](https://errbot.io/) plugin to get Graphs and Data from
[Netdata](https://github.com/firehol/netdata)

## Dependencies

  * Urllib3
  * Mathplotlib

## Installation
	
	Clone this repository intro the BOT_EXTRA_PLUGIN_DIR or
	use !repos install
## Commands
  
  * !netdata names - Get a list of Graphs from host
   * Options: 
	* host: Netdata host to querry
	* [--sheme SHEME]: Sheme of host. Either http or https. Default: http 
	* [--port PORT]: Port of Host. Default: 19999

  * !netdata chart - Get a Chart Plot from Host
   * Options: 
    * name: Name of Graph 
	* host: Netdata host
    * [--sheme SHEME]: Sheme of host. Either http or https. Default: http
	* [--port PORT]: Port of Host. Default: 19999
	* [--group GROUP]: The grouping method. Methods supported "min", "max", "average", "sum", "incremental-sum". Default value : average
	* [--points POINTS]: The number of points to be returned. If not given, or it is <= 0, or it is bigger than the points stored in the round robin database for this chart for the given duration, all the available collected values for the given duration will be returned. Default: 20 
	* [--after AFTER]: Can either be an absolute timestamp specifying the starting point of the data to be returned, or a relative number of seconds (negative, relative to parameter: before). Netdata will assume it is a relative number if it is less that 3 years (in seconds). Default: -600
	
  * netdata table - Get Data from Graph as Table.
   * Options:
    * name: Name of Graph 
	* host: Netdata host
    * [--sheme SHEME]: Sheme of host. Either http or https. Default: http
	* [--port PORT]: Port of Host. Default: 19999
	* [--group GROUP]: The grouping method. Methods supported "min", "max", "average", "sum", "incremental-sum". Default value : average
	* [--points POINTS]: The number of points to be returned. If not given, or it is <= 0, or it is bigger than the points stored in the round robin database for this chart for the given duration, all the available collected values for the given duration will be returned. Default: 20 
	* [--after AFTER]: Can either be an absolute timestamp specifying the starting point of the data to be returned, or a relative number of seconds (negative, relative to parameter: before). Netdata will assume it is a relative number if it is less that 3 years (in seconds). Default: -600
	
