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
import com.ericsson.procus.tpaf.report.Report;
import com.ericsson.procus.tpaf.utils.ModelException;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;

public class TPCreationJob extends JobBase{

	private HashMap<String, Object> options;
	private View view;
	private ModelInterface model;
	private String UID;
	private String finalMessage = "";
	private File outputDir;
	private Report report;
	
	public TPCreationJob(View view, ModelInterface model, HashMap<String, Object> options, File outputDir, Report report){
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
			
			Text ID = new Text("Creation of " + model.getTechPackName() + ": ");
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

		Text ID = new Text("Creation of " + model.getTechPackName() + ": ");
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

		Text ID = new Text("Creation of " + model.getTechPackName() + ": ");
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
		ArrayList<String> tasks = (ArrayList<String>)options.get("Create");
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

		if(!outputDir.exists()){
			outputDir.mkdirs();
		}
		String output = outputDir.getPath();
		
		try{
			String lockedDate = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
			String lockedBy = TPAFenvironment.USERNAME+"_"+TPAFenvironment.PRODUCTNAME+"_"+TPAFenvironment.PRODUCTRSTATE;
			lockedBy = lockedBy.replace(" ", "");
			model.updateLockedInfo(lockedBy, lockedDate);
			
			report.setCreatedInformation(lockedBy, lockedDate);
			report.setTechPackName(model.getTechPackName());
			report.setTPAFVersion(TPAFenvironment.PRODUCTRSTATE);
			report.setSupportedVendorReleases(model.getSupportedVendorReleases());
			
			updateProgress(0, 100);		
		
			if(server != null && !server.equals("")){
				updateMessage("Setting up the environment ("+counter+"/"+noOfTasks+")");
		    	model.setupENIQEnvironment(server, TPAFenvironment.ENVDIR);
		    	
		    	String ENIQversion = model.getServerENIQVersion(server);
		    	
		    	report.setServerInformation(server, ENIQversion);
		    	model.updateENIQversion(ENIQversion);
		    	
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Create_Tech_Pack")){
				updateMessage("Creating the Tech Pack ("+counter+"/"+noOfTasks+")");
		    	model.createTechPack(server);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Generate_Tech_Pack_Sets")){
				updateMessage("Generating the Tech Pack Sets ("+counter+"/"+noOfTasks+")");
		    	model.createTechPackSets(server, output);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Activate_Tech_Pack")){
				updateMessage("Activating the Tech Pack ("+counter+"/"+noOfTasks+")");
		    	model.activateTechPack(server);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Create_Tech_Pack_tpi_file")){
				updateMessage("Creating Tech Pack tpi file ("+counter+"/"+noOfTasks+")");
				String buildNumber = model.getTechPackName().split(":")[1];
				buildNumber = buildNumber.replace("((", "");
				buildNumber = buildNumber.replace("))", "");
				
				String encrypt = "False";
				if(tasks.contains("Encrypt_Tech_Pack_tpi")){
					encrypt = "True";
				}
		    	model.createTechPacktpi(server, Integer.valueOf(buildNumber), output, encrypt);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Create_Interfaces")){
				updateMessage("Creating Interfaces ("+counter+"/"+noOfTasks+")");
		    	model.createInterfaces(server);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Generate_Interface_Sets")){
				updateMessage("Creating the Interface sets ("+counter+"/"+noOfTasks+")");
		    	model.createInterfaceSets(server, output);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Activate_Interfaces")){
				updateMessage("Activating Interfaces ("+counter+"/"+noOfTasks+")");
		    	model.activateInterfaces(server);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Create_Interface_tpi_files")){
				updateMessage("Creating the Interface tpis ("+counter+"/"+noOfTasks+")");
				
				String encrypt = "False";
				if(tasks.contains("Encrypt_Interfaces_tpis")){
					encrypt = "True";
				}
		    	model.createInterfacetpis(server, output, encrypt);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Create_Tech_Pack_Description_Doc")){
				System.out.println("Create_Description_Doc");
				updateMessage("Creating the Tech Pack Description Document ("+counter+"/"+noOfTasks+")");
		    	model.createTechPackDescDoc(server, output);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Create_XLS_doc")){
				updateMessage("Creating the Tech Pack FD Document ("+counter+"/"+noOfTasks+")");
		    	model.createTechPackXLSDoc(TPAFenvironment.ENVBASEDIR, output);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			if(tasks.contains("Create_XML_doc")){
				updateMessage("Creating the Tech Pack XML Document ("+counter+"/"+noOfTasks+")");
		    	model.createTechPackXMlDoc(output);
		    	updateProgress(incremental*counter, 100);
		    	counter+=1;
			}
			
			
			report.generateReportFile();
			
		}catch(ModelException e){
			e.printStackTrace();
			finalMessage = e.getMessage();
			this.failed();
		}catch(Exception e){
			e.printStackTrace();
			finalMessage = e.getMessage();
			this.failed();
		}
		
		updateMessage("Creation Complete");
		updateProgress(100, 100);
		finalMessage = "Creation complete. Any output was created in " + outputDir;

		return null;
	}
	
}
