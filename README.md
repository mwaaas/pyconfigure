**FORK** from https://github.com/andreypopp/configure

**ORGINAL AUTHOR** Andrey Popp @andreypopp

YAML configuration library which provides:

  * interpolation for string configuration values

  * configuration inheritance

  * configuration composition

  * object level configuration (like construct this object by calling some
    function with some arguments)

Added features:

  * Python3 (Python2 no compatible any more).

  * Concatenate variables on configuration: 
		

		config_field:!concat var.in.python "/relative/path"


  * Support for implicit resolvers from PyYaml. 

  * Added concat implicit resolver: 

		config_field: var.in.python "/relative/path" 

Development takes place at https://github.com/alfred82santa/configure
