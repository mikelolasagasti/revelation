#include <Python.h>
#include "pygobject.h"

void authmanager_register_classes (PyObject *d);
extern PyMethodDef authmanager_functions[];

DL_EXPORT(void) initauthmanager(void) {
	PyObject *m, *d;

	init_pygobject();
	m = Py_InitModule("authmanager", authmanager_functions);
	d = PyModule_GetDict(m);

	authmanager_register_classes(d);

	if (PyErr_Occurred())
		Py_FatalError ("can't initialize module authmanager");
}

