
from .avmu_exceptions import *
from .avmu_library    import *


##
#  \addtogroup Python-API
#  @{
#
# @brief This is the general import for the entire avmu interface library.
#
#        It is located at the import path of `avmu` (e.g. `import avmu`).
#
#        By including this file, you include (by proxy) the \ref Python-OOP-API
#        and \ref Python-Basic-API contents, which are both wildcard imported (`from x import *`)
#        into this module's namespace.
#
#        Its contents are effectively:
#
#            from .avmu_library    import *
#            from .avmu_exceptions import *
#
#        In general, you should probably not directly import `avmu.avmu_library`, but rather
#        simply `import avmu`, and use it directly.
#
#
#
# @}
