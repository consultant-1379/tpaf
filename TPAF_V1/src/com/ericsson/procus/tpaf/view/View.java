package com.ericsson.procus.tpaf.view;

import java.util.ArrayList;

import javafx.geometry.Rectangle2D;
import javafx.geometry.Side;
import javafx.scene.Group;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.control.SplitPane;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TextField;
import javafx.scene.effect.GaussianBlur;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.stage.Screen;
import javafx.stage.Stage;

import com.ericsson.procus.tpaf.controller.Controller;
import com.ericsson.procus.tpaf.controller.HomeController;
import com.ericsson.procus.tpaf.controller.JobController;
import com.ericsson.procus.tpaf.controller.TpViewController;
import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.utils.CssHandler;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.elements.HomeView;
import com.ericsson.procus.tpaf.view.elements.IntroView;
import com.ericsson.procus.tpaf.view.elements.JobsView;
import com.ericsson.procus.tpaf.view.elements.TpView;

public class View{
	
    private double width;
    private double height;
	private CssHandler css;
	private IntroView introComponents;
	private Controller listener;
	private Stage primaryStage;
	BorderPane root;
	
	public View(Stage primaryStage){
		this.primaryStage = primaryStage;
		css = new CssHandler();
		introComponents = new IntroView();
	}
	
	public View(){}
	
	public Stage getStage(){
		return primaryStage;
	}

	public void show(Controller listener) {
		this.listener = listener;
		introComponents.setListener(listener);
		setDefaultDimensions();
		root = new BorderPane();
		root.getStyleClass().add(TPAFenvironment.BASE_BACKGROUND);
		root.setTop(introComponents.getTitleBar(""));
		
		showMainPageOptions();
		
		Scene scene = new Scene(root, width, height);
		scene.getStylesheets().add(css.getCssFileName());
		
		primaryStage.setTitle("Ericsson Tech Pack Automation Framework");
        primaryStage.setScene(scene);
        primaryStage.show();
		
	}
	
	public void showMainPageOptions(){
		root.setCenter(introComponents.getIntroPane());
	}
	
	public void showMainPageLoading(String style){
		VBox pane = (VBox)lookup("#BaseVBox");
		introComponents.getFDLoadOptions(pane, style);
	}
	
	public void addWaitMessage(){
		HBox pane = (HBox)lookup("#ServerLoadBase");
		introComponents.addWaitMessage(pane);
		
	}
	
	public void showTPfromServer(ArrayList<String> listofNames){
		HBox pane = (HBox)lookup("#ServerLoadBase");
		introComponents.showTPfromServer(pane, listofNames);
	}
	
	public void showTabbedViewBase(Controller homelistener, Controller jobslistener){
		TabPane tabPane = new TabPane();
		tabPane.setId("tabpane");
		HomeView home = new HomeView();
		home.setListener(homelistener);
		
		JobsView jobs = new JobsView();
		jobs.setListener(jobslistener);
		
		tabPane.getTabs().addAll(home.drawHomeTab(), jobs.drawJobsTab());
		tabPane.setSide(Side.LEFT);
		root.setCenter(tabPane);
	}
	
	public void createTpviewTab(TpViewController TPlistener, ModelInterface model){		
		TabPane tabPane = (TabPane)lookup("#tabpane");
		if(lookup("#"+model.getModelUID()+"_Tab")==null){
			TpView tpview = new TpView(model);
			tpview.setListener(TPlistener);
			Tab viewTab = tpview.drawTPviewTab();
			tabPane.getTabs().addAll(viewTab);
			tabPane.getSelectionModel().select(viewTab);
			TPlistener.setTpview(tpview);
		}else{	
			for(Tab tab: tabPane.getTabs()){
				System.out.println(tab.getId());
				System.out.println(model.getModelUID()+"_Tab");
				if(tab.getId() != null){
					if(tab.getId().equals(model.getModelUID()+"_Tab")){
						tabPane.getSelectionModel().select(tab);
					}
				}
			}
			
		}
	}
	
	public void applyBlurr(){
		root.setEffect(new GaussianBlur());
	}
	
	public void removeBlurr(){
		root.setEffect(null);
	}
	
	private void setDefaultDimensions(){
		//The percentage values are used as multipliers for screen width/height.
        double percentageWidth = 0.98;
        double percentageHeight = 0.90;
        //Calculate the width / height of screen.
        Rectangle2D screenSize = Screen.getPrimary().getBounds();
		width = percentageWidth * screenSize.getWidth();
		height = percentageHeight * screenSize.getHeight();
	}
	
	public Object lookup(String id){
		return primaryStage.getScene().lookup(id);
	}
		

}
