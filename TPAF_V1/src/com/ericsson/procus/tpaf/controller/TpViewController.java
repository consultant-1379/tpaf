package com.ericsson.procus.tpaf.controller;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;


import com.ericsson.procus.tpaf.controller.jobs.BOJob;
import com.ericsson.procus.tpaf.controller.jobs.DifferenceJob;
import com.ericsson.procus.tpaf.controller.jobs.TPCreationJob;
import com.ericsson.procus.tpaf.controller.jobs.DRTexecuteJob;
import com.ericsson.procus.tpaf.controller.jobs.JobScheduler;
import com.ericsson.procus.tpaf.controller.jobs.TPDeleteJob;
import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.report.Report;
import com.ericsson.procus.tpaf.utils.ModelException;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;
import com.ericsson.procus.tpaf.view.elements.TpView;
import com.ericsson.procus.tpaf.view.elements.options.DeleteFromServerOptions;
import com.ericsson.procus.tpaf.view.elements.options.DifferenceOptions;
import com.ericsson.procus.tpaf.view.elements.options.TpCreateOptions;
import com.sun.javafx.scene.control.skin.TitledPaneSkin;

import javafx.collections.ObservableList;
import javafx.event.Event;
import javafx.geometry.Insets;
import javafx.scene.Node;
import javafx.scene.control.Accordion;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Dialogs;
import javafx.scene.control.Label;
import javafx.scene.control.RadioButton;
import javafx.scene.control.TextField;
import javafx.scene.control.Dialogs.DialogOptions;
import javafx.scene.control.Dialogs.DialogResponse;
import javafx.scene.control.TitledPane;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.util.Callback;

public class TpViewController implements Controller{
	
	private ModelInterface model;
	private View view;
	private TpView tpview;
	private HashMap<String, ArrayList<String>> rulesToRun;
	private HashMap<String, HashMap<String, String>> rules;
	private Report report;
	
	public TpViewController(View view, ModelInterface model){
		this.model = model;
		this.view = view;
	}
	
	public void setTpview(TpView tpview){
		this.tpview = tpview;
	}
	
	
	@Override
	public void handle(Event event) {
		if (event.getSource() instanceof Text){
			Text e = (Text)event.getSource();
			if (e.getId().equalsIgnoreCase("reset")){
				System.setProperty("RulesLocation", "");
				BorderPane position = (BorderPane)view.lookup("#"+model.getModelUID()+"leftside");
				position.getChildren().removeAll(position.getChildren());
				System.setProperty(model.getModelUID()+"Rules", "Failed");
			}
		}
		if (event.getSource() instanceof Button){
			Button e = (Button)event.getSource();
			if (e.getId().equalsIgnoreCase("DesignRules")){
				if(view.lookup("#"+model.getModelUID()+"DesignRulesAccordion")==null){
					handleCreateScenario();
				}else{
					boolean minumumRules = false;
					rulesToRun = new HashMap<String, ArrayList<String>>();
					ObservableList<TitledPane> list = ((Accordion)view.lookup("#"+model.getModelUID()+"DesignRulesAccordion")).getPanes();
					for(TitledPane pane : list){
						ArrayList<String> rules = new ArrayList<String>();
						VBox content = (VBox)view.lookup("#"+model.getModelUID()+pane.getText()+"VBox");
						
						ObservableList<Node> checks = content.getChildrenUnmodifiable();
						for(Node node : checks){
							CheckBox check = (CheckBox)node;
							if(!check.getText().equalsIgnoreCase(" -> TOGGLE ALL") && check.isSelected()){
								String name = check.getText();
					        	name = name.replace(" ", "_");
					        	rules.add(name);
					        	minumumRules = true;
							}
						}
						rulesToRun.put(pane.getText(), rules);
					}
									
					if(minumumRules){
						report = new Report();
						report.setAllAvailableRules(rules);
						report.setExecutedRules(rulesToRun);
						JobScheduler.getInstance().scheduleJob(new DRTexecuteJob(view, model, rulesToRun));
					}else{
						Dialogs.showErrorDialog(view.getStage(), "No design rules have been selected", "DRT error","Error");
					}
				}
			}
			
			if (e.getId().equalsIgnoreCase("difference")){
				
				DifferenceOptions creation = new DifferenceOptions(view, this);
				ModelInterface selectedModel = creation.showOptionsWindow();
				if(selectedModel != null){
					String outputDir = TPAFenvironment.OUTPUTDIR+"\\"+model.getTechPackOutputName();
					outputDir = outputDir + "_" + new SimpleDateFormat("yyyyMMddHHmmss").format(new Date());
					File output = new File(outputDir);
					JobScheduler.getInstance().scheduleJob(new DifferenceJob(view, model, selectedModel, output));
				}
			}
			
			if (e.getId().equalsIgnoreCase("unsupported")){
				Dialogs.showWarningDialog(view.getStage(), "Place holder for future functionality", "Warning Dialog", "Unsupported Feature");
			}
			if (e.getId().equalsIgnoreCase("delete")){
				DeleteFromServerOptions delete = new DeleteFromServerOptions(view, this);
				HashMap<String, Object> results = delete.showOptionsWindow();
				if(!results.isEmpty()){
					if(results.containsKey("Delete")){
						if(!results.containsKey("ServerName")){
							Dialogs.showErrorDialog(view.getStage(), "A Server Name must be given for the selected tasks.\n\n" +
									"Deletion job will not be scheduled.", "Deletion error","Error");
						}else {
							JobScheduler.getInstance().scheduleJob(new TPDeleteJob(view, model, results));
						}
					}
				}
			}
			if (e.getId().equalsIgnoreCase("create")){
				TpCreateOptions creation = new TpCreateOptions(view, this);
				HashMap<String, Object> results = creation.showOptionsWindow();
				
				if(!results.isEmpty()){
					
					String outputDir = TPAFenvironment.OUTPUTDIR+"\\"+model.getTechPackOutputName();
					outputDir = outputDir + "_" + new SimpleDateFormat("yyyyMMddHHmmss").format(new Date());
					File output = new File(outputDir);
					
					if(report == null){
						report = new Report();
					}
					
					report.setOutputDirectory(output);
					report.clearCreatedfiles();
					
					if(results.containsKey("Create")){
						boolean requireEnv = false;
						ArrayList<String> items = (ArrayList<String>)results.get("Create");
						for(String item : creation.tpOptions){
							if(items.contains(item)){
								requireEnv = true;
							}
						}
						
						for(String item : creation.IntfOptions){
							if(items.contains(item)){
								requireEnv = true;
							}
						}
						
						if(items.contains("Create_Description_Doc")){
							requireEnv = true;
						}
	
						if(!results.containsKey("ServerName") && requireEnv){
							Dialogs.showErrorDialog(view.getStage(), "A Server Name must be given for the selected tasks.\n\n" +
									"Creation job will not be scheduled.", "Creation error","Error");
						}else {
							JobScheduler.getInstance().scheduleJob(new TPCreationJob(view, model, results, output, report));
						}
					}
					
					
					if(results.containsKey("BOjobType") || results.containsKey("UniDoc") || results.containsKey("Create_Verification_Reports")){
						if(results.containsKey("ODBCname") && results.containsKey("BISip") && results.containsKey("ServerName")){
							JobScheduler.getInstance().scheduleJob(new BOJob(view, model, results, output, report));
						}else{
							Dialogs.showErrorDialog(view.getStage(), "Required information for BO job not provided.\n\n" +
									"BO job will not be scheduled.", "Creation error","Error");
						}
					}

				}
			
			} 

		}else if(event.getSource() instanceof CheckBox){
			CheckBox cb = (CheckBox)event.getSource();
			if(cb.getText().equalsIgnoreCase("Create Tech Pack") || cb.getText().equalsIgnoreCase("Create Interfaces")){
				if(cb.isSelected()){
					if (System.getProperty(model.getModelUID()+"Rules", "Failed").equals("Passed")){
						ObservableList<Node> list = ((VBox)cb.getParent()).getChildren();
						for(Node node : list){
							if(node instanceof CheckBox){
								((CheckBox)node).setSelected(true);
							}
						}
						((CheckBox)cb.getScene().lookup("#Create_XLS_doc")).setSelected(true);
						((CheckBox)cb.getScene().lookup("#Create_XML_doc")).setSelected(true);
					}
					else{
						Dialogs.showErrorDialog(view.getStage(), "Can not create a Tech Pack/ Interface until DRT has passed", "DRT has not been passed", "Creation error");
						cb.setSelected(false);
					}
				}
				
			}else if(cb.getText().equalsIgnoreCase("Delete Tech Pack") || cb.getText().equalsIgnoreCase("Delete Interfaces")){
				if(cb.isSelected()){
					ObservableList<Node> list = ((VBox)cb.getParent()).getChildren();
					for(Node node : list){
						if(node instanceof CheckBox){
							((CheckBox)node).setSelected(true);
						}
					}
				}
				
			}else if(cb.getText().equalsIgnoreCase(" -> TOGGLE ALL")){
				Boolean status = cb.isSelected();
				cb.setIndeterminate(false);
				ObservableList<Node> list = ((VBox)cb.getParent()).getChildren();
				for(Node node : list){
					((CheckBox)node).setSelected(status);
				}
			}else{
				ObservableList<Node> list = ((VBox)cb.getParent()).getChildren();
				for(Node node : list){
					if(node instanceof CheckBox){
						CheckBox check = (CheckBox)node;
						if(check.getText().equalsIgnoreCase(" -> TOGGLE ALL")){
							check.setIndeterminate(true);
						}
					}
				}
			}	
			
		}
		
		else if(event.getSource() instanceof RadioButton){
			RadioButton rb = (RadioButton)event.getSource();
			if(rb.getText().equalsIgnoreCase("Create Universe") || rb.getText().equalsIgnoreCase("Update Universe")){
				((CheckBox)rb.getScene().lookup("#Create_Universe_Description_Doc")).setSelected(true);
				RadioButton BI4 = (RadioButton)rb.getScene().lookup("#BI_4");
				if (!BI4.isSelected()){
					((RadioButton)rb.getScene().lookup("#BI_3")).setSelected(true);
				}
			}
		}
		
	}
	
	private void handleCreateScenario(){
		BorderPane base = new BorderPane();
		if(System.getProperty("RulesLocation", "").equalsIgnoreCase("")){
			GridPane grid = new GridPane();
			grid.setHgap(10);
			grid.setVgap(10);
			grid.setPadding(new Insets(0, 10, 0, 10));
			
			final TextField location = new TextField();
			location.setPromptText("Rule Sets location");
			
			grid.add(new Label("Rule Sets path:"), 0, 0);
			grid.add(location, 1, 0);
			
			Callback<Void, Void> myCallback = new Callback<Void, Void>() {
				@Override
				public Void call(Void param) {
					System.setProperty("RulesLocation", location.getText());
					return null;
				}
			};
			base.setCenter(grid);

			DialogResponse resp = Dialogs.showCustomDialog(view.getStage(), base, "Please give the Rule Sets location", "DRT", DialogOptions.OK_CANCEL, myCallback);
		}
		
		if(!System.getProperty("RulesLocation", "").equalsIgnoreCase("")){
			try{
				rules = model.getRuleSetProperties(System.getProperty("RulesLocation"));
				BorderPane position = (BorderPane)view.lookup("#"+model.getModelUID()+"leftside");
				tpview.createDRTOptions(rules, position);
				
			}catch(ModelException e){
				String message = e.getMessage().substring(e.getMessage().lastIndexOf(":")+1, e.getMessage().length());
				Dialogs.showErrorDialog(view.getStage(), message, "DRT error","Error", e);
				System.setProperty("RulesLocation", "");
			}
			
		}
	}
	
	

	@Override
	public void execute() {}
	
}
