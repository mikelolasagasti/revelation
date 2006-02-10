/*
 *
 *  $Id$
 *  Copyright (C) 2001, Xavier Defrang <xavier_at_defrang_dot_com>
 *
 *  This program is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License
 *  as published by the Free Software Foundation; either version 2
 *  of the License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the FSF:
 *
 *      Free Software Foundation, Inc.,
 *      59 Temple Place - Suite 330, Boston, 
 *      MA 02111-1307, USA.
 *
 */


#include <Python.h>

#include <sys/mman.h>


/* Module Information */

static char __author__[] = "Xavier Defrang <xavier_at_defrang_dot_com>";
static char __version__[] = "$Revision$";


static char mlockall_docstring[] = "Locks in memory all pages mapped by an address space. See mlockall(2) for details.";

static PyObject *mman_mlockall(PyObject *self, PyObject *args)
{
	int flags, result;
	
	if (!PyArg_ParseTuple(args, "i", &flags)) 
		return NULL;

	result = mlockall(flags);

	return Py_BuildValue("i", (int)result);
}


static char munlockall_docstring[] = "Removes address space locks and locks on mappings in the address space. See mlockall(2) for details.";

static PyObject *mman_unmlockall(PyObject *self, PyObject *args)
{
	int result;
	
	result = munlockall();

	return Py_BuildValue("i", (int)result);
}

/* Module documentation */
static char mman_docstring[] = "Memory locking functions.";


/* Methods */
static PyMethodDef mman_methods[] = {
  { "mlockall", mman_mlockall, METH_VARARGS, mlockall_docstring },
  { "munlockall", mman_unmlockall, 0, munlockall_docstring },
  { NULL, NULL }  
};



/* Module intialization */
void initmman(void)
{
	PyObject *m;
	PyObject *d;
 
	/* Intialize module */
	m = Py_InitModule3("mman", mman_methods, mman_docstring);

	/* Get module namespace */
	d = PyModule_GetDict(m);

	/* Declare flags bitmasks */
	PyDict_SetItemString(d, "MCL_CURRENT", PyInt_FromLong(MCL_CURRENT));
	PyDict_SetItemString(d, "MCL_FUTURE", PyInt_FromLong(MCL_FUTURE));

	/* Set module information */
	PyDict_SetItemString(d, "__author__", PyString_FromString(__author__)); 
	PyDict_SetItemString(d, "__version__", PyString_FromString(__version__)); 
}

