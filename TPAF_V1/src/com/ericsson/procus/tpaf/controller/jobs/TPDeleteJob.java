package com.ericsson.procus.tpaf.controller.jobs;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.UUID;

import javafx.geometry.Insets;
import javafx.scene.control.ProgressBar;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;

import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.utils.ModelException;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;

public class TPDeleteJob extends JobBase{

	private HashMap<String, Object> options;
	private View view;
	private ModelInterface model;
	private String UID;
	private String finalMessage = "";
	
	public TPDeleteJob(View view, ModelInterface model, HashMap<String, Object> options){
		this.options = options;
		this.view = view;
		this.model = model;
		this.UID = String.valueOf(UUID.randomUUID());
	}
	
	
	@Override
	protected void scheduled() {
		super.scheduled();
		
		if((HBox) view.lookup("#" + UID) == null){

			HBox loader = new HBox();
			
			Text ID = new Text("Deletion of " + model.getTechPackName() + ": ");
			ID.setId("taskId");
			ID.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);
	
			loader.setId(UID);
			loader.setPadding(new Insets(20, 0, 0, 0));
			loader.setSpacing(10);
			loader.getChildren().addAll(ID);
	
			((VBox) view.lookup("#ongoingJobsVBox")).getChildren().addAll(loader);
		}
	}
	
	
	@Override
	protected void running(){
		super.running();
		
		ProgressBar bar = new ProgressBar();
		bar.setPrefHeight(20);
		bar.setPrefWidth(400);
		bar.progressProperty().bind(this.progressProperty());
		
		Text status = new Text("Loading");
		status.setId(UID + "_Status");
		status.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);
		status.textProperty().bind(this.messageProperty());
		
		((HBox) view.lookup("#" + UID)).getChildren().addAll(bar, status);
	}
	
	@Override
	protected void succeeded() {
		super.succeeded();
		
		HBox task = (HBox) view.lookup("#" + UID);
		((VBox) view.lookup("#ongoingJobsVBox")).getChildren().remove(task);

		HBox completedTask = new HBox();
		completedTask.setPadding(new Insets(20, 0, 0, 0));
		completedTask.setSpacing(10);

		Text ID = new Text("Deletion of " + model.getTechPackName() + ": ");
		ID.setId("taskId");
		ID.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		Text message = new Text(finalMessage);
		message.setId("taskId");
		message.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		completedTask.getChildren().addAll(ID, message);

		((VBox) view.lookup("#completedJobsVBox")).getChildren().addAll(
				completedTask);

		//Ask Garbage collector to run in the effort to save memory usage. 
		System.gc();
	}
	
	@Override
	protected void failed() {
		super.failed();
		
		HBox task = (HBox) view.lookup("#" + UID);
		((VBox) view.lookup("#ongoingJobsVBox")).getChildren().remove(task);

		HBox completedTask = new HBox();
		completedTask.setPadding(new Insets(20, 0, 0, 0));
		completedTask.setSpacing(10);

		Text ID = new Text("Deletion of " + model.getTechPackName() + ": ");
		ID.setId("taskId");
		ID.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		Text message = new Text(finalMessage);
		message.setId("taskId");
		message.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		completedTask.getChildren().addAll(ID, message);

		((VBox) view.lookup("#errorJobsVBox")).getChildren().addAll(
				completedTask);
		
		//Ask Garbage collector to run in the effort to save memory usage. 
		System.gc();
	}
	
	@Override
	protected Object call() throws Exception {
		String server = (String)options.get("ServerName");
		ArrayList<String> tasks = (ArrayList<String>)options.get("Delete");
		int incremental = 0;
		int noOfTasks = 0;
		if(server != null && !server.equals("")){
			incremental = 100/(tasks.size()+1);
			noOfTasks = tasks.size()+1;
		}else{
			incremental = 100/tasks.size();
			noOfTasks = tasks.size();
		}
		int counter = 1;
		
		try{			
			updateProgress(0, 100);
		
			if(server != null && !server.equals("")){
				updateMessage("Setting up the environment ("+counter+"/"+noOfTasks+")");
		    	model.setupENIQEnvironment(server, TPAFenvironment.ENVDIR);		    	
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Deactivate_Interfaces")){
				updateMessage("Deactivating the Interfaces ("+counter+"/"+noOfTasks+")");
		    	model.deActivateInterfaces(server);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Delete_Interfaces")){
				updateMessage("Deleting the Interfaces ("+counter+"/"+noOfTasks+")");
		    	model.deleteInterfaces(server);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Deactivate_Tech_Pack")){
				updateMessage("Deactivating the Tech Pack ("+counter+"/"+noOfTasks+")");
		    	model.deactivateTechPack(server);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Delete_Tech_Pack_sets")){
				updateMessage("Deleting the Tech Pack Sets ("+counter+"/"+noOfTasks+")");
		    	model.deleteSetsTechPack(server);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Delete_Tech_Pack")){
				updateMessage("Deleting the Tech Pack ("+counter+"/"+noOfTasks+")");
		    	model.deleteTechPack(server);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
		}catch(ModelException e){
			e.printStackTrace();
			finalMessage = e.getMessage();
			this.failed();
		}catch(Exception e){
			e.printStackTrace();
			finalMessage = e.getMessage();
			this.failed();
		}
		
		updateMessage("Deletion Complete");
		updateProgress(100, 100);
		finalMessage = "Deletion of " + model.getTechPackName() + " complete ";

		return null;
	}
	
}
