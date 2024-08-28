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
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;

import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.report.Report;
import com.ericsson.procus.tpaf.utils.ModelException;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;

public class BOJob extends JobBase{

	private HashMap<String, Object> options;
	private View view;
	private ModelInterface model;
	private String UID;
	private String finalMessage = "";
	private File outputDir;
	private Report report;
	
	public BOJob(View view, ModelInterface model, HashMap<String, Object> options, File outputDir, Report report){
		this.options = options;
		this.view = view;
		this.model = model;
		this.UID = String.valueOf(UUID.randomUUID());
		this.outputDir = outputDir;
		this.report = report;
	}
	
	
	@Override
	protected void scheduled() {
		super.scheduled();
		
		if((HBox) view.lookup("#" + UID) == null){

			HBox loader = new HBox();
			
			Text ID = new Text("BO task for " + model.getTechPackName() + ": ");
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

		Text ID = new Text("BO task for " + model.getTechPackName() + ": ");
		ID.setId("taskId");
		ID.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		Text message = new Text(finalMessage);
		message.setId("taskId");
		message.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		completedTask.getChildren().addAll(ID, message);

		((VBox) view.lookup("#completedJobsVBox")).getChildren().addAll(completedTask);

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

		Text ID = new Text("BO task for " + model.getTechPackName() + ": ");
		ID.setId("taskId");
		ID.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		Text message = new Text(finalMessage);
		message.setId("taskId");
		message.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		completedTask.getChildren().addAll(ID, message);

		((VBox) view.lookup("#errorJobsVBox")).getChildren().addAll(completedTask);
		
		//Ask Garbage collector to run in the effort to save memory usage. 
		System.gc();
		
	}
	
	@Override
	protected Object call() throws Exception {
		try{
			String server = (String)options.get("ServerName");
			String byjobType = (String)options.get("BOjobType");
			String ODBC = (String)options.get("ODBCname");
			String BISIP = (String)options.get("BISip");
			String BIversion = (String)options.get("BIversion");
			String UserName = (String)options.get("UserName");
			String Password = "";
			if(options.containsKey("Password")){
				Password = (String)options.get("Password");
			}
			String encrypt = "False";
			if(options.containsKey("Encrypt_Package")){
				encrypt = (String)options.get("Encrypt_Package");
			}
			
			report.setTechPackName(model.getTechPackName());
			report.setTPAFVersion(TPAFenvironment.PRODUCTRSTATE);
			report.setSupportedVendorReleases(model.getSupportedVendorReleases());
			report.setBODetails(byjobType, ODBC, BISIP, UserName, Password, BIversion);
			
			
			if(!outputDir.exists()){
				outputDir.mkdirs();
			}
			String output = outputDir.getAbsolutePath();
			
			
			int noOfSteps = 5;
			if(options.containsKey("UniDoc")){
				noOfSteps++;
			}
			
			updateProgress(0, 100);
		
			if(server != null && !server.equals("")){
				updateMessage("Setting up the environment (1/"+noOfSteps+")");
		    	model.setupENIQEnvironment(server, TPAFenvironment.ENVDIR);
		    	
		    	String ENIQversion = model.getServerENIQVersion(server);
				report.setServerInformation(server, ENIQversion);
		    	
		    	updateProgress((100/noOfSteps)*1, 100);
			}
			
			updateMessage("Initialising universe environment (2/"+noOfSteps+")");
			model.initBOUniverse(output, BIversion);
			updateProgress((100/noOfSteps)*2, 100);
			
			if(byjobType != null){
				if(byjobType.equals("Create")){
					updateMessage("Creating the universe (3/"+noOfSteps+")");
					model.createUniverse(BISIP, ODBC, server, UserName, Password);
					updateProgress((100/noOfSteps)*3, 100);
				}else if(byjobType.equals("Update")){
					updateMessage("Updating the universe (3/"+noOfSteps+")");
					model.updateUniverse(BISIP, ODBC, server, UserName, Password);
					updateProgress((100/noOfSteps)*3, 100);
				}
			}
			
			if(options.containsKey("Create_Verification_Reports")){
				updateMessage("Creating the verification reports (4/"+noOfSteps+")");
				model.createVerificationReports(BISIP, ODBC, server, UserName, Password);
				updateProgress((100/noOfSteps)*4, 100);
			}
			
			if(options.containsKey("Create_Package")){
				updateMessage("Creating BO Package (5/"+noOfSteps+")");
				model.createBOPackage(TPAFenvironment.USERNAME+"_"+TPAFenvironment.PRODUCTNAME+"_"+TPAFenvironment.PRODUCTRSTATE, encrypt);
				updateProgress((100/noOfSteps)*5, 100);
			}
			
			if(options.containsKey("UniDoc")){
				updateMessage("Creating the Universe Document (6/"+noOfSteps+")");
				model.createBOReferenceDoc(BISIP, ODBC, server, UserName, Password);
				updateProgress((100/noOfSteps)*6, 100);
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
		
		report.generateReportFile();
		
		updateMessage("Creation Complete");
		updateProgress(100, 100);
		finalMessage = "BO job completed. Any output was created in " + outputDir;

		return null;
	}
	
}
