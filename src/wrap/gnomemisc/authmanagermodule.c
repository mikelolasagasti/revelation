#include <Python.h>
#include "pygobject.h"

void gnomemisc_register_classes (PyObject *d);
extern PyMethodDef gnomemisc_functions[];

DL_EXPORT(void) initgnomemisc(void) {
	PyObject *m, *d;

	init_pygobject();
	m = Py_InitModule("gnomemisc", gnomemisc_functions);
	d = PyModule_GetDict(m);

	gnomemisc_register_classes(d);

	if (PyErr_Occurred())
		Py_FatalError ("can't initialize module gnomemisc");
}

