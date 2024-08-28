package com.ericsson.procus.tpaf.iconCreator;

import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.effect.Reflection;
import javafx.scene.layout.StackPane;
import javafx.scene.paint.Color;
import javafx.scene.paint.CycleMethod;
import javafx.scene.paint.LinearGradient;
import javafx.scene.paint.LinearGradientBuilder;
import javafx.scene.paint.RadialGradient;
import javafx.scene.paint.RadialGradientBuilder;
import javafx.scene.paint.Stop;
import javafx.scene.shape.Circle;
import javafx.scene.shape.CircleBuilder;
import javafx.scene.shape.Ellipse;
import javafx.scene.shape.EllipseBuilder;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;
import javafx.stage.Stage;

public class IconCreator2 extends Application {

	int radius = 250;
	int cx = 100;
	int cy = 100;
	Color base = Color.BLUE;
	//Color ambient = Color.rgb(6/255, 76/255, 160/255, 127/255.0);
	Color ambient = Color.DODGERBLUE;
	Color specular = Color.rgb(64/255, 142/255, 203/255);
	Color shine = Color.WHITE;
	
	@Override
	public void start(Stage primaryStage) {
		primaryStage.setTitle("TPAF Icon");
		StackPane root = new StackPane();
		root.setStyle("-fx-background-color: white");
		
		int height = radius * 2;
		Color specular2 = Color.rgb(64/255, 142/255, 203/255, 0.0 );  
		Color shine1 = new Color(1.0, 1.0, 1.0, 0.5 );  
		Color shine2 = new Color(1.0, 1.0, 1.0,  0.0 ); 
		
		
		RadialGradient gradient1 = new RadialGradient(25, 0, 0, 0, radius, false, CycleMethod.NO_CYCLE, new Stop[] {
				new Stop(0.0, Color.WHITE),
				new Stop(0.2, Color.LIGHTBLUE),
				 new Stop(0.4, Color.DODGERBLUE),
	            new Stop(1, Color.DARKBLUE)
	        });
		
		
		
		Circle circle = CircleBuilder.create()
				.centerX(cx)
				.centerY(cy)
				.radius(radius)
				.fill(gradient1)
				.build();
		
		RadialGradient radial = RadialGradientBuilder.create()
				.proportional(false)
				.centerX(cx)
				.centerY(cy)
				.radius(radius)
				.stops(new Stop(0.0, ambient ), 
					new Stop(1.0, Color.color(0,0,0,0.8)))
				.build();
		
		Circle circle1 = CircleBuilder.create()
				.centerX(cx)
				.centerY(cy)
				.radius(radius)
				.fill(radial)
				.build();
		
		Text name = new Text("TP AF");
		name.setFill(Color.WHITE);
		//name.setStroke(Color.GREY);
		name.setFont(Font.font("ERICSSON CAPITAL TT", FontWeight.THIN, 160));
		
		
		
		root.getChildren().addAll(circle, name);

        primaryStage.setScene(new Scene(root, 810, 810));
        primaryStage.show();
	}

	public static void main(String[] args) {
		launch(args);
	}
}
