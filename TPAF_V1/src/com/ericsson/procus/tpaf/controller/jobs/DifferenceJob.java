package com.ericsson.procus.tpaf.controller.jobs;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
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

public class DifferenceJob extends JobBase{

	private View view;
	private ModelInterface baseModel;
	private String UID;
	private String finalMessage = "";
	private File outputDir;
	private ModelInterface diffModel;
	
	public DifferenceJob(View view, ModelInterface basemodel, ModelInterface diffModel, File outputDir){
		this.view = view;
		this.baseModel = basemodel;
		this.diffModel = diffModel;
		this.UID = String.valueOf(UUID.randomUUID());
		this.outputDir = outputDir;
	}
	
	
	@Override
	protected void scheduled() {
		super.scheduled();
		
		if((HBox) view.lookup("#" + UID) == null){

			HBox loader = new HBox();
			
			Text ID = new Text("Running Comparison: ");
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

		Text ID = new Text("Comparison complete: ");
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

		Text ID = new Text("Comparison failed: ");
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
		if(!outputDir.exists()){
			outputDir.mkdirs();
		}
		String output = outputDir.getAbsolutePath();
		int noOfDiffs = 0;
		updateProgress(0, 100);
		try{
			updateMessage("Running Comparison of "+baseModel.getTechPackName() + " and " + diffModel.getTechPackName());
			noOfDiffs = baseModel.runDifference(diffModel, output);
	    	updateProgress(80, 100);
			
		}catch(ModelException e){
			e.printStackTrace();
			finalMessage = e.getMessage();
			this.failed();
		}catch(Exception e){
			e.printStackTrace();
			finalMessage = e.getMessage();
			this.failed();
		}
		
		updateMessage("Comparison Complete");
		updateProgress(100, 100);
		if(noOfDiffs > 0){
			finalMessage = "Comparison of "+baseModel.getTechPackName() + " and " + diffModel.getTechPackName() + 
					". "+ noOfDiffs +" found, results file was created in " + outputDir;
		}else{
			finalMessage = "Comparison of "+baseModel.getTechPackName() + " and " + diffModel.getTechPackName() + 
					". 0 differences found";
		}
		
		System.out.println(finalMessage);
		
		return null;
	}
	
}