package com.ericsson.procus.tpaf.controller.jobs;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.SortedSet;
import java.util.TreeSet;
import java.util.UUID;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressBar;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.Separator;
import javafx.scene.control.Tooltip;
import javafx.scene.control.ScrollPane.ScrollBarPolicy;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;
import javafx.scene.layout.ColumnConstraints;
import javafx.scene.layout.ColumnConstraintsBuilder;

import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.utils.ModelException;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;

public class DRTexecuteJob extends JobBase{
	
	private View view;
	private ModelInterface model;
	private HashMap<String, ArrayList<String>> rulesToRun;
	private String UID;
	private String finalMessage = "";
	private HashMap<String, HashMap<String, ArrayList<String>>> errors;
	
	public DRTexecuteJob(View view, ModelInterface model, HashMap<String, ArrayList<String>> rulesToRun){
		this.view = view;
		this.model = model;
		this.rulesToRun = rulesToRun;
		this.UID = String.valueOf(UUID.randomUUID());
	}
	
	@Override
	protected void scheduled() {
		super.scheduled();
		if((HBox) view.lookup("#" + UID) == null){
			HBox loader = new HBox();
			Text ID = new Text("Applying design rules to " + model.getTechPackName()+ ": ");
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

		Text ID = new Text("Design rules applied to " + model.getTechPackName()+ ": ");
		ID.setId("taskId");
		ID.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		Text message = new Text(finalMessage + " errors found");
		message.setId("taskId");
		message.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.SMALLFONT);

		completedTask.getChildren().addAll(ID, message);

		((VBox) view.lookup("#completedJobsVBox")).getChildren().addAll(completedTask);
		
		
		VBox base = new VBox();
		base.setSpacing(3);
		
		Label Title = new Label("Design Rules Results");
		Title.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.MEDIUMFONT);
	    
		StackPane stack = new StackPane();
	    stack.getChildren().addAll(Title);
	    stack.setAlignment(Pos.CENTER);
	    stack.setPadding(new Insets(0, 0, 15, 0));
	    base.getChildren().addAll(stack);
	    
	    ScrollPane scrollpane = new ScrollPane();
	    scrollpane.setPrefViewportHeight(800);
	    scrollpane.setFitToHeight(true);
	    scrollpane.setFitToWidth(true);
	    scrollpane.setContent(base);
	    scrollpane.setHbarPolicy(ScrollBarPolicy.AS_NEEDED);
	    scrollpane.setVbarPolicy(ScrollBarPolicy.AS_NEEDED);
	    
		if(errors.size() == 0){ 
		    Label passed = new Label("No errors found");
		    passed.getStyleClass().addAll(TPAFenvironment.MEDIUMFONT, TPAFenvironment.GREENFONT);
		    
		    StackPane passedstack = new StackPane();
			passedstack.getChildren().addAll(passed);
			passedstack.setAlignment(Pos.CENTER);
			passedstack.setPadding(new Insets(15, 0, 15, 0));
		    base.getChildren().addAll(passedstack);
		    
		    System.setProperty(model.getModelUID()+"Rules", "Passed");
		    
		}else{
			System.setProperty(model.getModelUID()+"Rules", "Failed");
			SortedSet<String> keys = new TreeSet<String>(errors.keySet());
			for (String key : keys) {
				String name = key;
				name = name.replace("_", " ");
				
				HBox RNbase = new HBox();
				RNbase.setSpacing(3);
				
				Label RuleName = new Label(name + ": ");
				RuleName.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.MEDIUMFONT);
				RNbase.getChildren().addAll(RuleName);
				base.getChildren().addAll(RNbase, new Separator());
	
				GridPane errorItems = new GridPane();
				errorItems.setPadding(new Insets(0, 10, 30, 10));
	
				ColumnConstraints widthconstraint = ColumnConstraintsBuilder.create().percentWidth(50).build();
				errorItems.getColumnConstraints().addAll(widthconstraint,widthconstraint);
	
				VBox col1 = new VBox();
				col1.setSpacing(5);
				col1.setPadding(new Insets(5, 5, 5, 5));
	
				VBox col2 = new VBox();
				col2.setSpacing(5);
				col2.setPadding(new Insets(5, 5, 5, 5));
			    
			    HashMap<String, ArrayList<String>> errorCollection = errors.get(key);
			    SortedSet<String> errorMessages = new TreeSet<String>(errorCollection.keySet());
			    int count = 0;
				for (String errorMessage : errorMessages) {
					
					StackPane errorMessageStack = new StackPane();
					errorMessageStack.setAlignment(Pos.BOTTOM_CENTER);
					
					Label RuleMessage = new Label(errorMessage);
					RuleMessage.getStyleClass().addAll(TPAFenvironment.SMALLFONT, TPAFenvironment.REDFONT);
					errorMessageStack.getChildren().addAll(RuleMessage);
					RNbase.getChildren().addAll(errorMessageStack);
			        
			        ArrayList<String> items = errorCollection.get(errorMessage);
			        for(String item: items){
			        	String[] itemParts = item.split("-");
			        	String itemName = itemParts[itemParts.length-1].split("=")[1];
			        	String itemLocation = "";
			        	for(String part : itemParts){
			        		itemLocation = itemLocation + part + " -> ";
			        	}
			        	itemLocation = itemLocation.substring(0, itemLocation.lastIndexOf(" -> "));
	
				        Label label = new Label(itemName);
				        label.getStyleClass().addAll(TPAFenvironment.GREENFONT, TPAFenvironment.SMALLFONT);
				        label.setTooltip(new Tooltip(itemLocation));
				        label.setWrapText(true);
				    	
				    	int row = 0;
				    	if(count % 2 == 0){
				    		col1.getChildren().addAll(label);
				    		row = col1.getChildren().size()/2;
				    	}else if(count % 2 == 1){
				    		col2.getChildren().addAll(label);
				    		row = col2.getChildren().size()/2;
				    	}
				    	count = count + 1;
				    }
			    }
			    
			    errorItems.getChildren().addAll(col1, col2);
				GridPane.setConstraints(col1, 0, 0);
				GridPane.setConstraints(col2, 1, 0);
			    
				base.getChildren().addAll(errorItems);
		        
		    }
		}
		
		((BorderPane)view.lookup("#"+model.getModelUID()+"leftside")).setCenter(scrollpane);
		
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

		Text ID = new Text("Applying design rules to " + model.getTechPackName()+ ": ");
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
		errors = new HashMap<String, HashMap<String, ArrayList<String>>>();
		
		int incremental = 100/rulesToRun.size();
		int counter = 0;
		
		Iterator it = rulesToRun.entrySet().iterator();
	    while (it.hasNext()) {
	        Map.Entry pairs = (Map.Entry)it.next();
	        counter+=1;
	        String moduleName = (String)pairs.getKey();
	        ArrayList<String> rulestoRun = (ArrayList<String>)pairs.getValue();
	        
	        try{
		        updateMessage("Executing "+moduleName);
		        errors.putAll(model.executeRules(moduleName, rulestoRun));
		        updateProgress(incremental*counter, 100);
	        }catch(ModelException e){
				finalMessage = e.getMessage();
				this.failed();
			}
	        
	        finalMessage = ""+errors.size();
	        
	        it.remove(); // avoids a ConcurrentModificationException
	    }
	      
		return null;
	}
	

}
