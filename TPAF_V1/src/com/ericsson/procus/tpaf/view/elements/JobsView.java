package com.ericsson.procus.tpaf.view.elements;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.ScrollPane.ScrollBarPolicy;
import javafx.scene.control.Separator;
import javafx.scene.control.Tab;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.ColumnConstraints;
import javafx.scene.layout.ColumnConstraintsBuilder;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.RowConstraints;
import javafx.scene.layout.RowConstraintsBuilder;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;

import com.ericsson.procus.tpaf.controller.Controller;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;

public class JobsView {
	
	private Controller listener;

	public void setListener(Controller listener){
		this.listener = listener;
	}
	
	public Tab drawJobsTab(){
		Tab Taskstab = new Tab("Jobs");
		Taskstab.setClosable(false);
		
		BorderPane base = new BorderPane();
		
		GridPane groups = new GridPane();
		groups.getStyleClass().add(TPAFenvironment.BASE_BACKGROUND);
		groups.setId("groups");
		
		VBox ongoingtasks = createGrouping("Ongoing jobs", "ongoingJobsVBox", false);
		VBox completedtasks = createGrouping("Completed jobs", "completedJobsVBox", true);
		VBox errortasks = createGrouping("Failed jobs", "errorJobsVBox", true);
		
		groups.getChildren().addAll(ongoingtasks, completedtasks, errortasks);
	    GridPane.setConstraints(ongoingtasks, 0, 0);
	    GridPane.setConstraints(completedtasks, 0, 1);
	    GridPane.setConstraints(errortasks, 0, 2);
		
		RowConstraints heightconstraint = RowConstraintsBuilder.create().percentHeight(35).build();
		groups.getRowConstraints().addAll(heightconstraint, heightconstraint, heightconstraint);
		
		ColumnConstraints widthconstraint = ColumnConstraintsBuilder.create().percentWidth(100).build();
		groups.getColumnConstraints().addAll(widthconstraint);
		
		base.setCenter(groups);
		
		Taskstab.setContent(base);
		
		return Taskstab;
	}
	
	
	private VBox createGrouping(String title, String id, boolean clearoption){
		VBox base = new VBox();
		base.getStyleClass().add(id);
		base.setPadding(new Insets(0, 10, 0, 5));
		
		Text Title = new Text(title);
	    Title.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.LARGEFONT);			    
	    
	    VBox jobsbase = new VBox();
	    jobsbase.setSpacing(10);
	    jobsbase.setId(id);
	    
	    StackPane stack = new StackPane();
	    
	    ScrollPane scrollpane = new ScrollPane();
	    scrollpane.getStyleClass().add(TPAFenvironment.FDLOAD);
	    scrollpane.setPrefViewportHeight(300);
	    scrollpane.setFitToWidth(true);
	    scrollpane.setContent(jobsbase);
	    scrollpane.setHbarPolicy(ScrollBarPolicy.AS_NEEDED);
	    scrollpane.setVbarPolicy(ScrollBarPolicy.AS_NEEDED);
	    stack.getChildren().addAll(scrollpane);
	    
	    if(clearoption){
			HBox titlebase = new HBox();
			BorderPane clearBase = new BorderPane();
			
			Text clear = new Text("Clear list");
			clear.setId(id+"_clear");
			clear.getStyleClass().addAll(TPAFenvironment.BLACKFONT, TPAFenvironment.MEDIUMFONT);
			clear.setOnMouseClicked(listener);
			
			clearBase.setLeft(Title);
		    clearBase.setRight(clear);

			base.getChildren().addAll(clearBase, new Separator(), stack);
		}
	    else{
	    	base.getChildren().addAll(Title, new Separator(), stack);
	    }
		
	    return base;
	}
	
	
	
}
