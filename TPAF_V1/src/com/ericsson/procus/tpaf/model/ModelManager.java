package com.ericsson.procus.tpaf.model;


import javafx.collections.FXCollections;
import javafx.collections.ObservableList;

public class ModelManager {
	
	private static ModelManager mm;
	private static int instance;
	public ObservableList<ModelInterface> data;
	
	private ModelManager(){
		mm = this;
		data = FXCollections.observableArrayList();
	}
	
	public void addToList(ModelInterface model){
		data.add(model);
	}
	
	public ModelInterface getFromList(int index){
		return data.get(index);
	}
	
	public void removeFromList(ModelInterface tp){
		data.remove(tp);
	}
	
	public ObservableList<String> getLoadedmodelInfo(){
		ObservableList<String> info = FXCollections.observableArrayList();
		for(ModelInterface model : data){
			String title = model.getTechPackName() + " : " + model.getLoadSource();
			info.add(title);
		}
		return info;
	}
	
	public static ModelManager getInstance(){
		if(instance ==0){
			instance = 1;
			return new ModelManager();
		}
		if(instance == 1){
			return mm;
		}
		
		return null;
	}
}
