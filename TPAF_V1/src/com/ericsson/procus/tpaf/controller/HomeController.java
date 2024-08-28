package com.ericsson.procus.tpaf.controller;

import java.io.File;
import java.util.HashMap;

import com.ericsson.procus.tpaf.controller.jobs.FDLoadJob;
import com.ericsson.procus.tpaf.controller.jobs.JobBase;
import com.ericsson.procus.tpaf.controller.jobs.JobScheduler;
import com.ericsson.procus.tpaf.controller.jobs.ServerLoadJob;
import com.ericsson.procus.tpaf.controller.jobs.TpiLoadJob;
import com.ericsson.procus.tpaf.controller.jobs.XMLLoad;
import com.ericsson.procus.tpaf.model.ModelFactory;
import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.model.ModelManager;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;
import com.ericsson.procus.tpaf.view.elements.TpView;
import com.ericsson.procus.tpaf.view.elements.options.LoadTPfromServer;

import javafx.event.Event;
import javafx.scene.control.Button;
import javafx.scene.control.Dialogs;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.Dialogs.DialogOptions;
import javafx.scene.control.Dialogs.DialogResponse;
import javafx.scene.control.TablePosition;
import javafx.scene.control.TableView;
import javafx.stage.FileChooser;

public class HomeController implements Controller{

	private View view;
	private ModelFactory modelcreator;
	public HomeController(ModelFactory modelcreator, View view){
		this.view = view;
		this.modelcreator = modelcreator;
	}

	@Override
	public void handle(Event event) {
		if (event.getSource() instanceof Button){
			Button e = (Button)event.getSource();
			if(e.getId().equalsIgnoreCase("FDLoad") || e.getId().equalsIgnoreCase("tpiLoad") || e.getId().equalsIgnoreCase("xmlLoad")){
				view.applyBlurr();
				FileChooser fileChooser = new FileChooser();
				fileChooser.setTitle("Open Input File");
				FileChooser.ExtensionFilter extFilter = null;
				if(e.getId().equalsIgnoreCase("FDLoad")){
					extFilter = new FileChooser.ExtensionFilter("FD (*.xls)", "*.xls");
				}else if(e.getId().equalsIgnoreCase("tpiLoad")){
					extFilter = new FileChooser.ExtensionFilter("tpi (*.tpi)", "*.tpi");
				}else if(e.getId().equalsIgnoreCase("xmlLoad")){
					extFilter = new FileChooser.ExtensionFilter("xml (*.xml)", "*.xml");
				}
				fileChooser.getExtensionFilters().add(extFilter);
				File file = fileChooser.showOpenDialog(view.getStage());
				view.removeBlurr();
                if (file != null) { 
                	JobBase job = null;
                	String location = file.getAbsolutePath();
                	if(location.endsWith(".xls")){
						job = new FDLoadJob(view, location, modelcreator);
					}else if(location.endsWith(".xml")){
						job = new XMLLoad(view, location, modelcreator);
					}else if(location.endsWith(".tpi")){
						job = new TpiLoadJob(view, location, modelcreator);
					}
                	
                	JobScheduler.getInstance().scheduleJob(job);
                }
			}
			
			if(e.getId().equalsIgnoreCase(TPAFenvironment.SERVERLOAD)){
				view.applyBlurr();
				LoadTPfromServer load = new LoadTPfromServer(view, modelcreator);
				HashMap<String, String>results = load.showLoadingWindow();
				view.removeBlurr();
				if(results.containsKey("ServerName") && results.containsKey("TPName")){
					JobScheduler.getInstance().scheduleJob(new ServerLoadJob(view, results.get("ServerName"), results.get("TPName"), modelcreator));
				}
				
			}
			
			if (e.getId().equalsIgnoreCase("remove")){
				TableView<ModelInterface> table = (TableView<ModelInterface>)view.lookup("#LoadedTable");
				
				ModelInterface techpack = table.getSelectionModel().getSelectedItem();
				
				DialogResponse response = Dialogs.showConfirmDialog(view.getStage(), "Are you sure you want to remove "+ techpack.getTechPackName()+"?",
					      "Confirm Dialog", "Remove TechPack", DialogOptions.OK_CANCEL);
				
				if(response == DialogResponse.OK){
					 ModelManager.getInstance().removeFromList(techpack);
				}
			}
			
			if (e.getId().equalsIgnoreCase("view")){
				TableView<ModelInterface> table = (TableView<ModelInterface>)view.lookup("#LoadedTable");
				ModelInterface model = table.getSelectionModel().getSelectedItem();
				
				TpViewController tpviewcontroller = new TpViewController(view, model);
				view.createTpviewTab(tpviewcontroller, model);
			}
			
			if (e.getId().equalsIgnoreCase("unsupported")){
				Dialogs.showWarningDialog(view.getStage(), "Currently not supported by TP AF", "Warning Dialog", "Unsupported Feature");
			}
			
			
		}
		
	}
	
	
	@Override
	public void execute() {
		// TODO Auto-generated method stub
		
	}
	

}
