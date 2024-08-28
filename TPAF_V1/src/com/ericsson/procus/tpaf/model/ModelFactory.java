package com.ericsson.procus.tpaf.model;

import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

import java.net.URL;
import java.net.URLClassLoader;


public class ModelFactory {
	
	private PyObject builder;
	
	public void init(){
		PythonInterpreter interpreter = new PythonInterpreter();
    	ClassLoader cl = ClassLoader.getSystemClassLoader();
    	URL[] urls = ((URLClassLoader)cl).getURLs();
    	
    	interpreter.exec("import sys");
        for(URL url: urls){
        	String path = url.getFile().substring(1);
        	interpreter.exec("sys.path.append('"+path+"')");
        }
        interpreter.exec("from modelInterface import modelInterface");
        builder = interpreter.get("modelInterface");
	}
	
	public ModelInterface create() {
        PyObject buildingObject = builder.__call__();
        return (ModelInterface)buildingObject.__tojava__(ModelInterface.class);
    }
	
}
