import React from 'react';
import SliderHome from '../inc/SliderHome'


class Home extends React.Component{
    render(){
        return( 
            <div>
                <h2>Home Page</h2>
                <SliderHome />
                <button className="btn btn-primary">Bootstrap Button Sample</button>
            </div>
        );
    }
}

export default Home; 