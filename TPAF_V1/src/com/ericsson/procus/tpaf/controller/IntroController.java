package com.ericsson.procus.tpaf.controller;

import java.io.File;
import java.util.ArrayList;

import com.ericsson.procus.tpaf.controller.jobs.FDLoadJob;
import com.ericsson.procus.tpaf.controller.jobs.JobBase;
import com.ericsson.procus.tpaf.controller.jobs.JobScheduler;
import com.ericsson.procus.tpaf.controller.jobs.ServerLoadJob;
import com.ericsson.procus.tpaf.controller.jobs.TpiLoadJob;
import com.ericsson.procus.tpaf.controller.jobs.XMLLoad;
import com.ericsson.procus.tpaf.model.ModelFactory;
import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.view.View;

import javafx.event.Event;
import javafx.scene.control.Button;
import javafx.scene.control.Dialogs;
import javafx.scene.control.RadioButton;
import javafx.scene.control.TextField;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.stage.FileChooser;

public class IntroController implements Controller{

	private View view;
	private ModelFactory modelcreator;
	private String ServerTPLoadname;
	
	public IntroController(ModelFactory modelcreator, View view){
		this.modelcreator = modelcreator;
		this.view = view;
	}
	
	@Override
	public void execute() {
		view.show(this);
	}
	
	@Override 
	public void handle(Event event) {
		
		if (event.getSource() instanceof Button){
			Button e = (Button)event.getSource();
			if (e.getId().equalsIgnoreCase("loadOption")){
				String style = e.getStyleClass().get(1);
				view.showMainPageLoading(style);
			}
		}
		
		if (event.getSource() instanceof RadioButton){
			RadioButton e = (RadioButton)event.getSource();
			ServerTPLoadname = e.getText().replace(" ", "_");
		}
		
		if (event.getSource() instanceof Text){
			Text e = (Text)event.getSource();
			if (e.getId().equalsIgnoreCase("back")){
				view.showMainPageOptions();
			}
			else if(e.getId().equalsIgnoreCase("FDLoad") || e.getId().equalsIgnoreCase("tpiLoad") || e.getId().equalsIgnoreCase("xmlLoad")){
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
                	((TextField)view.lookup("#input")).setText(file.getPath());
                }
			}
			else if(e.getId().equalsIgnoreCase("serverLoad")){
				view.addWaitMessage();
				final ArrayList<String> ListofNames = new ArrayList<String>();

				new Thread(new Runnable() {
	                public void run() {
	                	Object obj = view.lookup("#input");
	    				final String location = ((TextField)obj).getText();
	    				modelcreator.init();
	    				ModelInterface model = modelcreator.create();
	    				ListofNames.addAll(model.getTPNameFromServer(location));
	    				view.showTPfromServer(ListofNames);
	                }
	            }).start();
			}
			else if(e.getId().equalsIgnoreCase("Load")){
				Object obj = view.lookup("#input");
				JobBase job = null;
				if(obj instanceof TextField){
					final String location = ((TextField)obj).getText();
					
					if(location.length()>1){
						HomeController homelistener = new HomeController(modelcreator, view);
						JobController joblistener = new JobController(modelcreator, view);
						view.showTabbedViewBase(homelistener, joblistener);

						if(location.endsWith(".xls")){
							job = new FDLoadJob(view, location, modelcreator);
						}else if(location.endsWith(".xml")){
							job = new XMLLoad(view, location, modelcreator);
						}else if(location.endsWith(".tpi")){
							job = new TpiLoadJob(view, location, modelcreator);
						}else{
							job = new ServerLoadJob(view, location, ServerTPLoadname, modelcreator);
						}
						
						JobScheduler.getInstance().scheduleJob(job);
					}else{
						Dialogs.showErrorDialog(view.getStage(), "A source must be given to load fom\n\n" +
								"Load job will not be scheduled.", "Load error","Error");
					}
					
				}
				
			}

		}

		
	}
	


}
