package com.ericsson.procus.tpaf.controller.jobs;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.UUID;

import javafx.geometry.Insets;
import javafx.scene.control.ProgressBar;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;

import com.ericsson.procus.tpaf.model.ModelFactory;
import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.model.ModelManager;
import com.ericsson.procus.tpaf.utils.ModelException;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;

public class FDLoadJob extends JobBase{

	private String fileLocation;
	private View view;
	private ModelFactory modelcreator;
	private String UID;
	private String finalMessage = "";
	
	public FDLoadJob(View view, String fileLocation, ModelFactory modelcreator){
		this.fileLocation = fileLocation;
		this.view = view;
		this.modelcreator = modelcreator;
		this.UID = String.valueOf(UUID.randomUUID());
	}
	
	@Override
	protected void scheduled() {
		super.scheduled();
		
		if((HBox) view.lookup("#" + UID) == null){

			HBox loader = new HBox();
			
			Text ID = new Text("Load from " + new File(fileLocation).getName()+ ": ");
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

		Text ID = new Text("Load from " + new File(fileLocation).getName()
				+ ": ");
		ID.setId("taskId");
		ID.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		Text message = new Text(finalMessage + " loaded succesfully");
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

		Text ID = new Text("Load from " + new File(fileLocation).getName()+ ": ");
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
		ModelInterface model = null;
		try{
			updateProgress(0, 100);
			updateMessage("Initialising the model");
	    	modelcreator.init();
	    	updateProgress(10, 100);
	    	
	    	updateMessage("Creating model instance");
	    	model = modelcreator.create();
			updateProgress(25, 100);
		
		
			updateMessage("Parsing FD into dictionary");
			model.loadDictionaryFromFD(fileLocation);
			updateProgress(80, 100);
			
			updateMessage("Populating model from xls dictionary");
			model.populateModelFromFDdictionary();
			updateProgress(90, 100);
		}catch(ModelException e){
			finalMessage = e.getMessage();
			this.failed();
		}catch(Exception e){
			finalMessage = e.getMessage();
			e.printStackTrace();
			this.failed();
		}
		
		
		updateMessage("Adding to Model collection");
		
		model.setLoadSource(fileLocation);
		
		Date date = new Date();
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy/MM/dd HH:mm");
		model.setLoadDate(sdf.format(date));
		
		ModelManager.getInstance().addToList(model);
		updateProgress(100, 100);
		
		updateMessage("Load Complete");
		
		finalMessage = model.getTechPackName();
		
		return null;
	}
	
	
}
